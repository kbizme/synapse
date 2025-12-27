const input = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages-container');
const welcomeMessage = document.getElementById('welcome-message');
const chatUl = document.getElementById('chat-list');
const noChatsBanner = document.getElementById('no-chats-banner');

let CURRENT_CHAT_ID;



// page onload events and functions
document.addEventListener('DOMContentLoaded', async () => {
    // loading the chat history
    await LoadChatLists();

    // handling page load
    const params = new URLSearchParams(window.location.search);
    const chat_id = params.get('chat_id');
    // handling current chat
    if (chat_id) {
        LoadCurrentChats(chat_id);
    } else {
        createNewChat();
    }
});



// Allow 'Enter' key to send
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});


// send message
function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    // removing the intial greeting
    if (messagesContainer.children.length === 1) {
        messagesContainer.innerHTML = '';
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
    messagesContainer.appendChild(userDiv);

    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

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
        aiDiv.className = "message-bubble assistant-msg";
        aiDiv.innerHTML = marked.parse(data.reply, {breaks: true, gfm: true});
        messagesContainer.appendChild(aiDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;


        // updating the chat lists
        LoadChatLists();
    })
    .catch(err => {
        console.error(err);
    });

}



function createNewChat() {
    // clearing active chat marker
    ClearActiveChats();
    // initializing new chat id
    CURRENT_CHAT_ID = crypto.randomUUID();
    // clearing URL 
    history.pushState({}, "", "/");

    // displaying welcome message
    messagesContainer.innerHTML = `
        <div id="welcome-message">
            <img src="/static/images/synapse.png" alt="Synapse Logo"/>
            <p>Hello, How can I help you today?</p>
        </div>
    `;

    // changint the tab title
    document.title = "Synapse";

    // focuing on input
    input.focus();
}


// handling previous chats and chat history

async function LoadChatLists() {
    const res = await fetch("http://localhost:8000/all-chats");
    const data = await res.json();
    RenderChatLists(data.chats);
    HighlightActiveChat();
}

function RenderChatLists(all_chats){
    chatUl.innerHTML = '';
    if (!all_chats || all_chats.length === 0){
        console.log('no chats found');
        noChatsBanner.style.display = 'block';
        chatUl.style.display = 'none';
        createNewChat();
        return;
    };

    // otherwise, if previous chat found
    noChatsBanner.style.display = 'none';
    chatUl.style.display = 'block';
    
    all_chats.forEach(chat => {
        const item = document.createElement('li')
        item.textContent = chat.title;
        item.classList.add('chat-item');
        item.setAttribute('id', chat.id);
        item.setAttribute('title', chat.title);
        chatUl.appendChild(item);
        item.addEventListener('click', (e) => {
            ClearActiveChats();
            e.currentTarget.classList.add('active');
            // loading this clicked chat
            LoadCurrentChats(chat.id);
        });
    });
        
}


function ClearActiveChats(){
    const activeChats = document.querySelectorAll('.chat-item');
    activeChats.forEach(chat => {
        chat.classList.remove('active');
    });
}


function HighlightActiveChat(chat_id=undefined){
    // retrieving the chat id
    if (!chat_id){
        chat_id = CURRENT_CHAT_ID;
        if (!chat_id){
            const params = new URLSearchParams(window.location.search);
            chat_id = params.get('chat_id');
        };
    }
    try{
        document.getElementById(chat_id).classList.add('active');
    }catch(err){
        console.error(err);
    }
}


function LoadCurrentChats(chat_id){
    // updating current chat id
    CURRENT_CHAT_ID = chat_id;

    // making the current chat active
    // document.getElementById(chat_id).classList.add('active');
    HighlightActiveChat(chat_id);



    // updating the URL (no reload)
    history.pushState(
        { chat_id },
        "",
        `/?chat_id=${chat_id}`
    );
    // renaming the pate title
    // fetching the current chat
    fetch(`http://localhost:8000/chat/${chat_id}`)
    .then(res => res.json())
    .then(data => {
        document.title = data.chat_title;
        RenderCurrentChatMessages(data);
    });
}



function RenderCurrentChatMessages(chat_data){
    if (!chat_data || !chat_data.messages || chat_data.messages.length === 0) {
        messagesContainer.innerHTML = "<p>No messages yet</p>";
        return;
    }

    // updating the current chat id
    CURRENT_CHAT_ID = chat_data.id;
    
    // clearing the message container
    messagesContainer.innerHTML = '';

    // rendering the current chat messages inside the container
    chat_data.messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = msg.role === 'user' ? 'message-bubble user-msg' : 'message-bubble assistant-msg';
        div.innerHTML = marked.parse(msg.content, {breaks: true, gfm: true});
        messagesContainer.appendChild(div);
    });

}
