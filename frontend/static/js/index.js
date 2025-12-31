const input = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages-container');
const welcomeMessage = document.getElementById('welcome-message');
const chatUl = document.getElementById('chat-list');
const noChatsBanner = document.getElementById('no-chats-banner');


let CURRENT_CHAT_ID;
let PENDING_FILE = null;


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


// to handle the spacer when resizing, trivial
window.addEventListener('resize', () => {
    const spacer = document.getElementById('chat-spacer');
    if (spacer && spacer.style.height !== '0px') {
        spacer.style.height = `${messagesContainer.clientHeight}px`;
    }
});

// Allow 'Enter' key to send
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') HandleSend();
});


async function HandleSend(){
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

    const fileToSend = PENDING_FILE;

    // removing the welcome box
    const welcome = document.getElementById("welcome-message");
    if (welcome) welcome.remove();

    // clearing input text box
    input.value = '';

    // updating the URL (no reload)
    history.pushState(
        { CURRENT_CHAT_ID },
        "",
        `/?chat_id=${CURRENT_CHAT_ID}`
    );

    // calling the appropriate sendmessage function
    await SendMessage(text, fileToSend);
    // clearing the file chip
    removePendingFile();


    // updating the chat lists
    setTimeout(()=>{
        LoadChatLists();
    }, 500);
}



//////////////////// STREAMING RESPONSE ////////////////////
async function SendMessage(prompt, file=null){
    RenderUserMessage(prompt);

    // creating assistant message container
    const assistantDiv = document.createElement('div');
    assistantDiv.className = 'message-bubble assistant-msg';
    
    // inserting the assistant bubble before the spacer
    const spacer = document.getElementById('chat-spacer');
    messagesContainer.insertBefore(assistantDiv, spacer);

    let fetchOptions = {};
    let url = '';

    // DYNAMIC SELECTION
    if (file) {
        // Path A: Multipart for Files
        url = 'http://localhost:8000/chat/upload-and-query';
        const formData = new FormData();
        formData.append('chat_id', CURRENT_CHAT_ID);
        formData.append('message', prompt);
        formData.append('file', file);
        
        fetchOptions = {
            method: 'POST',
            body: formData 
        };
    } else {
        // Path B: Standard JSON for Text
        url = 'http://localhost:8000/chat/';
        fetchOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: CURRENT_CHAT_ID,
                message: prompt
            })
        };
    }

    /// hitting the backend api
    try {
        const response = await fetch(url, fetchOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // calling stream processing function
        await ProcessStream(response, assistantDiv);

    } catch (error) {
        console.error("Fetch error:", error);
        assistantDiv.innerHTML = "Sorry, something went wrong. Please try again.";
    }    
}


// this function renders the received streamed response
async function ProcessStream(response, assistantDiv) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantText = '';
    const spacer = document.getElementById('chat-spacer');
    const initialSpacerHeight = spacer ? parseInt(spacer.style.height) : 0;

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (value) {
            const chunk = decoder.decode(value, { stream: true });
            assistantText += chunk;
        }

        assistantDiv.innerHTML = marked.parse(assistantText, {breaks: true, gfm: true});
        
        if (spacer) {
            // As the assistant message grows, shrink the spacer by that amount
            const currentMessageHeight = assistantDiv.offsetHeight;
            const newHeight = Math.max(0, initialSpacerHeight - currentMessageHeight);
            spacer.style.height = `${newHeight}px`;
        }
    }

    // removing the spacer after response is complete
    if (spacer) {
        spacer.style.transition = 'height 0.4s ease-out';
        spacer.style.height = '0px';
        setTimeout(() => spacer.remove(), 400);
    }
}

//////////////////////////////////////////////////////////////////////////////////

function createNewChat() {
    // clearing active chat marker
    ClearActiveChats();
    // resetting the cyrrent chat id
    CURRENT_CHAT_ID = null;
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
    await RenderChatLists(data.chats);
}

async function RenderChatLists(all_chats){
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
    
    // highliting current chat
    HighlightActiveChat();
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
        if (chat_id){
            const currentChatLi = document.getElementById(chat_id)
            currentChatLi.classList.add('active');
            document.title = currentChatLi.getAttribute('title');

        }
    }catch(err){
        console.error(err);
    }
}


function LoadCurrentChats(chat_id){
    // updating current chat id
    CURRENT_CHAT_ID = chat_id;

    // making the current chat active
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
        if (msg.role === 'tool') return;
        if (msg.role === 'assistant'){
            if (msg.content === 'Searching my tools...' || msg.tool_calls){
                console.log('here');
                return;
            }
        }
        if (!msg.content) return;

        // now, constructing the message bubble
        const div = document.createElement('div');
        div.className = msg.role === 'user' ? 'message-bubble user-msg' : 'message-bubble assistant-msg';
        div.innerHTML = marked.parse(msg.content, {breaks: true, gfm: true});
        messagesContainer.appendChild(div);
    });
    ScrollToBottom();

}




function RenderUserMessage(text){
    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'message-bubble user-msg';
    userDiv.innerText = text;
    messagesContainer.appendChild(userDiv);
    input.value = '';
    
    // spacer 
    let spacer = document.getElementById('chat-spacer');
    if (spacer) spacer.remove(); 
    
    spacer = document.createElement('div');
    spacer.id = 'chat-spacer';

    // setting height to slightly less than container to keep the message perfectly at top
    const spacerGap = 100;
    spacer.style.height = `${messagesContainer.clientHeight - spacerGap}px`;
    messagesContainer.appendChild(spacer);

    // forcing the browser to recalculate the height
    setTimeout(() => {
        const gap = 30;
        const targetTop = userDiv.offsetTop - gap;
        messagesContainer.scrollTo({
            top: targetTop,
            behavior: 'smooth' 
        });
    }, 0);

}

function ScrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    console.log('i ran')
}



// File Upload Handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    PENDING_FILE = file; 
    
    // clearing the bar
    const previewBar = document.getElementById('file-preview-bar');
    previewBar.innerHTML = ''; 

    // shwoing selected file preview with a remove option
    const chip = document.createElement('div');
    chip.className = `file-chip ready`;
    chip.innerHTML = `
        <span>📄 ${file.name}</span>
        <span class="remove-file" onclick="removePendingFile()">×</span>
    `;
    previewBar.appendChild(chip);
    // resetting the file input value
    event.target.value = '';
}

function removePendingFile() {
    PENDING_FILE = null;
    document.getElementById('file-preview-bar').innerHTML = '';
}