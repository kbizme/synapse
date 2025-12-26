const input = document.getElementById('user-input');
const container = document.getElementById('messages-container');
const welcomeMessage = document.getElementById('welcome-message');
let CURRENT_CHAT_ID;



// Allow 'Enter' key to send
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});


// send message
function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    // removing the intial greeting
    if (container.children.length === 1) {
        container.innerHTML = '';
    }

    // checking if current chat id is initialized
    if (!CURRENT_CHAT_ID || typeof CURRENT_CHAT_ID !== 'string'){
        CURRENT_CHAT_ID = crypto.randomUUID();
    }

    // removing the welcome box
    if (welcomeMessage) welcomeMessage.remove();
    
    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'message-bubble user-msg';
    userDiv.innerText = text;
    container.appendChild(userDiv);

    input.value = '';
    container.scrollTop = container.scrollHeight;

    // sending the api request
    fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            chat_id: CURRENT_CHAT_ID,
            message: text
        })
    })
    .then(res => res.json())
    .then(data => {
        const aiDiv = document.createElement("div");
        aiDiv.className = "message-bubble ai-msg";
        aiDiv.innerText = data.reply;
        container.appendChild(aiDiv);
        container.scrollTop = container.scrollHeight;
    })
    .catch(err => {
        console.error(err);
    });

}



function createNewChat() {
    // if chat exists, then reseting the memory of that chat
    if (CURRENT_CHAT_ID) {
        fetch("http://localhost:8000/reset", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: CURRENT_CHAT_ID })
        }).catch(console.error);
    }

    // initializing new chat id
    CURRENT_CHAT_ID = crypto.randomUUID();

    container.innerHTML = `
        <div id="welcome-message">
            <img src="static/images/synapse.png" alt="Synapse Logo"/>
            <p>Hello, How can I help you today?</p>
        </div>
    `;
}

