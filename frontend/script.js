serverURL = "ws://localhost:8080/chat";
var socket = null

function showSignupPage() {
  document.getElementById("signup-page").style.display = "block";
  document.getElementById("login-page").style.display = "none";
  document.getElementById("add-contact-page").style.display = "none";
}

function showLoginPage() {
  document.getElementById("signup-page").style.display = "none";
  document.getElementById("login-page").style.display = "block";
  document.getElementById("add-contact-page").style.display = "none";
}

function showChatPage() {
  document.getElementById("signup-page").style.display = "none";
  document.getElementById("login-page").style.display = "none";
  document.getElementById("add-contact-page").style.display = "none";
}
function showAddContactPage() {
  document.getElementById("signup-page").style.display = "none";
  document.getElementById("login-page").style.display = "none";
  document.getElementById("add-contact-page").style.display = "block";
}

window.onload = function () {
  showLoginPage();
};



/*
{
    "action": "signup",
    "user_id": "sravan",
    "password": "sravan",
    "displayname": "sravan",
    "displaypicture": ""
}
{
    "action": "login",
    "user_id": "sravan",
    "password": "sravan"
}
{
    "action": "message",
   "msg_to": "vinay",
   "message": "hello Vinay"
}

{
    "action": "add_contact",
   "contacts": ["vinay"]
}
*/




/*
<div class="message-box message-recv">
  <span class="message text-recv"> I'm good, thanks! How about you? </span>
</div>
*/
// {
//   "action": "message",
//   "message": "Hello Sravan babu",
//   "msg_from": "bindu",
//   "msg_to": "sravan",
//   "msg_id": "5fa7e0dd-4267-493d-a5b4-7165ab0da1c8"
// }

function fillMessageBox(messages, append) {
  const chatBox = document.getElementById("chat-box");
  if (!append) {
    chatBox.innerHTML = "";
  }
  messages.forEach(message => {
    const messageBox = document.createElement("div");
    const user_id = getUserID()
    messageBox.classList.add("message-box")

    const messageElement = document.createElement("span");
    messageElement.classList.add("message")
    messageElement.innerText = message.message;
    messageElement.id = message.msg_id
    if (message.msg_to == user_id){
      messageBox.classList.add("message-recv")
      messageElement.classList.add("text-recv")
    } else{
      messageBox.classList.add("message-send")
      messageElement.classList.add("text-send")
    }

    messageBox.appendChild(messageElement)
    chatBox.appendChild(messageBox);
  });
  chatBox.scrollTop = chatBox.scrollHeight;
}

function setSelectedContact(contact){
  console.log(contact)
  document.getElementById("selected-user").value = contact;
}

function getSelectedContact() {
  return document.getElementById("selected-user").value;
}

function getUserID() {
  return document.getElementById("profile-name").value;
}

function setUserID(userID) {
  document.getElementById("profile-name").value = userID;
}

function fillContactBox(contacts, append) {
  const contactsBox = document.getElementById("contacts-list");
  if (!append) {
    contactsBox.innerHTML = "";
  }
  
  contacts.forEach(contact => {
    const contactBox = document.createElement("li");
    contactBox.classList.add("contact");

    const image = document.createElement("img");
    image.src = "images/user_profile.png";
    image.classList.add("contact-photo");

    const name = document.createElement("span");
    name.classList.add("contact-name")
    name.innerText = contact
    name.id = contact
    name.addEventListener("click", (event) => {
      selectContact(contact);
    });

    contactBox.appendChild(image)
    contactBox.appendChild(name)
    contactsBox.appendChild(contactBox);
  });
  contactsBox.scrollTop = contactsBox.scrollHeight;
}

function handleServerResponse(data) {
  let action = data.action
  if (action == "signup") {
    console.log(data)
    sendRequest({"action": "get_details"})
    sendRequest({"action": "get_chat"})
    showChatPage();
  }
  else if (action == "login") {
    console.log(data)
    sendRequest({"action": "get_details"})
    sendRequest({"action": "get_chat"})
    showChatPage();
  }
  else if (action == "get_details") {
    console.log(data)
    details = data.data
    const contacts = details.contacts
    setSelectedContact(contacts[0])
    fillContactBox(contacts, false)
  }
  else if (action == "get_chat") {
    const chats = data.data
    console.log(chats)
    let messages = []
    const contact = getSelectedContact()
    if (contact != null || contact != "") {
      messages = chats[contact]
    }
    else{
      for(let name in chats) {
        setSelectedContact(name)
        messages = chats[name]
        break;
      }
    }
    
    fillMessageBox(messages, false)
    // 
  }
  else if (action == "message") {
    fillMessageBox([data], true)
    console.log(data)
  }
  else if (action == "add_contact") {
    console.log(data)
  }

}

function connectToServer(action, username, password, displayname) {
  socket = new WebSocket(serverURL); // Replace with your server address

  setUserID(username)
  document.getElementById("profile-name").innerText = username
  socket.addEventListener("open", (event) => {
    console.log("WebSocket connection opened:", event);
    let data = {
      "action": action,
      "user_id": username,
      "password": password,
      "displayname": displayname
    }
    socket.send(JSON.stringify(data));
  });

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    handleServerResponse(message)
  });

  socket.addEventListener("close", (event) => {
    console.log("WebSocket connection closed:", event);
  });
}

function sendRequest(data) {
    socket.send(JSON.stringify(data));
}

function login() {
  const username = document.getElementById("login-username").value
  const password = document.getElementById("login-password").value
  const displayname = document.getElementById("signup-displayname").value
  connectToServer("login", username, password, "")
  showChatPage()
}

function signup() {
  const username = document.getElementById("signup-username").value
  const password = document.getElementById("signup-password").value
  const displayname = document.getElementById("signup-displayname").value
  connectToServer("signup", username, password, displayname)
  showChatPage()
}

function sendMessage() {
  const messageBox = document.getElementById("message-input")
  const message = messageBox.value
  messageBox.value = ""
  const data = {
    "action": "message",
    "message": message,
    "msg_to": getSelectedContact()
  }
  console.log(data)
  fillMessageBox([data], true)
  sendRequest(data)
}

function selectContact(contact) {
  setSelectedContact(contact)
  const data = {
    "action": "get_chat",
    "contacts": [contact]
  }
  console.log(data);
  sendRequest(data);
}

function addContact() {
  let contact = document.getElementById("add-contact-username").value;
  const data = {
    "action": "add_contact",
    "contacts": [contact]
  }
  sendRequest(data);
  showChatPage();
  fillContactBox([contact], true);
}

// connectToServer("login", "Sravan", "sravan", "")