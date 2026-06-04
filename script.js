if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
    .then(() => console.log("Service Worker Registered!"))
    .catch(err => console.error("Service Worker Failed", err));
}

document.addEventListener("DOMContentLoaded", () => {

    let currentUserEmail = null; 
    let tokenClient; 
    let currentCalendarEvents = [];

    window.onload = function () {
        // 1. Google Identity (For Login)
        google.accounts.id.initialize({
            client_id: "587589370747-hhhn90kv03r8vno3hkn2olcobaahi5an.apps.googleusercontent.com", 
            callback: handleCredentialResponse
        });
        
        google.accounts.id.renderButton(
            document.getElementById("google-btn"),
            { theme: "outline", size: "large", shape: "pill", width: 250 }  
        );
        
        google.accounts.id.prompt(); 

        // 2. Google OAuth2 (For Calendar Access)
        tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: "587589370747-hhhn90kv03r8vno3hkn2olcobaahi5an.apps.googleusercontent.com",
            scope: "https://www.googleapis.com/auth/calendar.readonly",
            callback: async (tokenResponse) => {
                if (tokenResponse && tokenResponse.access_token) {
                    console.log("Calendar permission granted!");
                    await syncCalendarWithBackend(tokenResponse.access_token);
                }
            }
        });
    };

    async function handleCredentialResponse(response) {
        const responsePayload = decodeJwtResponse(response.credential);
        console.log("Logged in as: " + responsePayload.name);
        currentUserEmail = responsePayload.email;

        try {
            await fetch("http://127.0.0.1:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: responsePayload.email,
                    name: responsePayload.name
                })
            });
        } catch (error) {
            console.error("Failed to sync user with backend.", error);
        }

        document.getElementById("login-screen").style.display = "none";
        document.getElementById("main-dashboard").style.display = "block";

        gsap.from(".dashboard-card", {
            y: 40, opacity: 0, duration: 0.8, ease: "expo.out"
        });
    }

    // Helper function to decode Google's JWT token
    function decodeJwtResponse(token) {
        let base64Url = token.split('.')[1];
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        let jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    }

    const updateClock = () => {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // Convert 0 to 12
        minutes = minutes < 10 ? '0' + minutes : minutes;
        
        document.getElementById("live-clock").innerText = `${hours}:${minutes} ${ampm}`;
    };
    
    setInterval(updateClock, 1000);
    updateClock();

    // --- Live Weather Logic (Vancouver) ---
    const fetchWeather = async () => {
        try {
            const res = await fetch("https://api.open-meteo.com/v1/forecast?latitude=49.2827&longitude=-123.1207&current_weather=true");
            const data = await res.json();
            
            const temp = Math.round(data.current_weather.temperature);
            document.getElementById("live-weather").innerText = `${temp}°C`;
        } catch (error) {
            console.error("Failed to fetch weather", error);
            document.getElementById("live-weather").innerText = "--°C";
        }
    };

    fetchWeather();
    setInterval(fetchWeather, 30 * 60 * 1000);

    const tl = gsap.timeline();
    tl.from(".nav-item", { y: -20, opacity: 0, duration: 0.6, stagger: 0.1, ease: "power3.out" });
    tl.from(".dashboard-card", { y: 40, opacity: 0, duration: 0.8, ease: "expo.out" }, "-=0.4");

    // --- Chat & Direction Logic ---
    const askBtn = document.getElementById("ask-btn");
    const inputField = document.getElementById("user-question");
    const responsePanel = document.getElementById("response-panel");
    const recText = document.getElementById("res-recommendation");
    const reasonText = document.getElementById("res-reasoning");
    const btnUbc = document.getElementById("btn-to-ubc");
    const btnHome = document.getElementById("btn-to-home");

    let currentDirection = "UBC"; 

    btnUbc.addEventListener("click", () => {
        currentDirection = "UBC";
        btnUbc.classList.add("active");
        btnHome.classList.remove("active");
    });

    btnHome.addEventListener("click", () => {
        currentDirection = "Home";
        btnHome.classList.add("active");
        btnUbc.classList.remove("active");
    });

    askBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        
        const question = inputField.value.trim();
        const currentWeather = document.getElementById("live-weather").innerText;

        if (!question) return;

        askBtn.classList.add("loading");
        inputField.disabled = true;

        if (responsePanel.style.display === "block") {
            await gsap.to(responsePanel, { opacity: 0, y: 10, duration: 0.2 });
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email : currentUserEmail,
                    question: question,
                    weather: currentWeather,
                    direction: currentDirection,
                    events: currentCalendarEvents
                })
            });
            
            const data = await response.json();
            
            recText.innerText = "Live Commute Plan";
            reasonText.innerText = data.reply;
            
        } catch (error) {
            recText.innerText = "Connection Error";
            reasonText.innerText = "Could not reach the backend. Is your Uvicorn server running?";
        }

        askBtn.classList.remove("loading");
        inputField.disabled = false;
        inputField.value = ""; 

        responsePanel.style.display = "block";
        
        gsap.fromTo(responsePanel, 
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }
        );
        
        gsap.fromTo([".response-header", ".recommendation", ".reasoning", ".tags-container"],
            { opacity: 0, y: 10 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.1, ease: "power2.out", delay: 0.2 }
        );
    });

    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            askBtn.click();
        }
    });

    // --- Modal UI Logic ---
    const settingsBtn = document.getElementById("settings-btn");
    const settingsModal = document.getElementById("settings-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const saveSettingsBtn = document.getElementById("save-settings-btn");

    if(settingsBtn) settingsBtn.addEventListener("click", () => settingsModal.classList.remove("hidden"));
    if(closeModalBtn) closeModalBtn.addEventListener("click", () => settingsModal.classList.add("hidden"));

    if(saveSettingsBtn) {
        saveSettingsBtn.addEventListener("click", async (e) => {
            e.preventDefault();

            const homeAddress = document.getElementById("home-address").value;
            const schoolAddress = document.getElementById("school-address").value;
            
            if (!currentUserEmail) {
                alert("You must be logged in to save settings!");
                return;
            }

            saveSettingsBtn.innerText = "Locating Coordinates...";
            saveSettingsBtn.disabled = true;

            try {
                const response = await fetch("http://127.0.0.1:8000/update-settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: currentUserEmail,
                        home_address: homeAddress,
                        school_address: schoolAddress
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    alert("Success! Your locations are locked in.");
                    settingsModal.classList.add("hidden");
                } else {
                    alert("Error: " + data.error);
                }
            } catch (error) {
                console.error("Geocoding failed:", error);
                alert("Server connection failed. Is Uvicorn running?");
            } finally {
                saveSettingsBtn.innerText = "Save Locations";
                saveSettingsBtn.disabled = false;
            }
        });
    }

    // --- NEW: Calendar Sync Logic ---
    const syncCalendarBtn = document.getElementById("sync-calendar-btn");
    const calendarWidget = document.getElementById("calendar-widget");
    const eventsList = document.getElementById("events-list");

    if (syncCalendarBtn) {
        syncCalendarBtn.addEventListener("click", () => {
            if (!currentUserEmail) {
                alert("Please log in first!");
                return;
            }
            // Triggers the Google popup asking for Calendar access
            tokenClient.requestAccessToken();
        });
    }

    async function syncCalendarWithBackend(accessToken) {
        syncCalendarBtn.innerText = "Syncing...";
        syncCalendarBtn.disabled = true;

        try {
            const response = await fetch("http://127.0.0.1:8000/sync-calendar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: currentUserEmail,
                    access_token: accessToken
                })
            });

            const data = await response.json();

            if (response.ok && data.events && data.events.length > 0) {
                currentCalendarEvents = data.events; 
                eventsList.innerHTML = "";
                
                data.events.forEach(event => {
                    const li = document.createElement("li");
                    const dateObj = new Date(event.start);
                    const timeString = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    
                    li.innerHTML = `
                        <span class="event-name">${event.title}</span>
                        <span class="event-time">${timeString}</span>
                    `;
                    eventsList.appendChild(li);
                });

                calendarWidget.style.display = "block";
                gsap.fromTo(calendarWidget, 
                    { opacity: 0, y: 20 }, 
                    { opacity: 1, y: 0, duration: 0.5 }
                );
                
            } else {
                alert("No upcoming events found today!");
            }
        } catch (error) {
            console.error("Calendar sync failed:", error);
            alert("Failed to connect to the server.");
        } finally {
            syncCalendarBtn.innerText = "📅 Sync Calendar";
            syncCalendarBtn.disabled = false;
        }
    }
});