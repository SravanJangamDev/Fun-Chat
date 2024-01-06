var userMessages = {};

serverURL = "wss://app.loan2wheels.com/chat";
var socket = new WebSocket(serverURL);
socket.addEventListener("open", (event) => {
  console.log("WebSocket connection opened:", event);
});

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  handleServerResponse(message);
});

socket.addEventListener("close", (event) => {
  console.log("WebSocket connection closed:", event);
});

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

function hideAddContactPage() {
  document.getElementById("add-contact-page").style.display = "none";
}

function hideStatusBox() {
  document.getElementById("status-msg-page").style.display = "none";
}

function displayError(error_msg) {
  document.getElementById("status-msg-page").style.display = "block";
  document.getElementById("status-msg").innerText = error_msg;
}

function showAddContactPage() {
  document.getElementById("signup-page").style.display = "none";
  document.getElementById("login-page").style.display = "none";
  document.getElementById("add-contact-page").style.display = "block";
}

function showMessageInputBox() {
  document.getElementById("message-input-box").style.display = "block";
}

function hideMessageInputBox() {
  document.getElementById("message-input-box").style.display = "none";
}

window.onload = function () {
  hideMessageInputBox();
  hideStatusBox();
  showLoginPage();
  // showChatPage();
};

function fillMessageBox(messages, append) {
  const chatBox = document.getElementById("chat-box");
  if (!append) {
    chatBox.innerHTML = "";
  }
  messages.forEach((message) => {
    const sent_by = message.sent_by;
    const selected_contact = getSelectedContact();
    if (selected_contact != sent_by) {
      return;
    }
    const messageBox = document.createElement("div");
    const user_id = getUserID();
    messageBox.classList.add("message-box");

    const messageElement = document.createElement("span");
    messageElement.classList.add("message");
    messageElement.innerText = message.message_text;
    messageElement.id = message.message_id;

    const timeElement = document.createElement("span");
    timeElement.classList.add("small-text");
    timeElement.innerText = message.timestamp;

    if (message.sent_to == user_id) {
      messageBox.classList.add("message-recv");
      messageElement.classList.add("text-recv");
      messageBox.appendChild(timeElement);
      messageBox.appendChild(messageElement);
    } else {
      messageBox.classList.add("message-send");
      messageElement.classList.add("text-send");
      messageBox.appendChild(messageElement);
      messageBox.appendChild(timeElement);
    }

    chatBox.appendChild(messageBox);
  });
  chatBox.scrollTop = chatBox.scrollHeight;
}

function setSelectedContact(contact) {
  console.log(contact);
  document.getElementById("selected_contact").value = contact;
}

function getSelectedContact() {
  return document.getElementById("selected_contact").value;
}

function getUserID() {
  return document.getElementById("user_id").value;
}

function setProfileName(profile_name) {
  document.getElementById("profile-name").innerText = profile_name;
}
function setUserID(userID) {
  document.getElementById("user_id").value = userID;
}

function fillContactBox(contacts, append) {
  const contactsBox = document.getElementById("contacts-list");
  if (!append) {
    contactsBox.innerHTML = "";
  }

  contacts.forEach((contact) => {
    const contactBox = document.createElement("li");
    contactBox.classList.add("contact");

    const image = document.createElement("img");
    image.src = "images/user_profile.png";
    image.classList.add("contact-photo");

    const name = document.createElement("span");
    name.classList.add("contact-name");
    name.innerText = contact.nickname;
    name.id = contact.contact_number;
    name.addEventListener("click", (event) => {
      showUserChat(contact.contact_number);
    });

    contactBox.appendChild(image);
    contactBox.appendChild(name);
    contactsBox.appendChild(contactBox);
  });
  contactsBox.scrollTop = contactsBox.scrollHeight;
}

function handleServerResponse(resp) {
  console.log(resp);
  const action = resp.action;
  const data = resp.data;
  const msg = resp.msg;
  const status = resp.status;
  if (status != 200) {
    console.log(msg);
    displayError(msg);
    return;
  }
  if (action == "signup") {
    socket.close();
    showLoginPage();
  } else if (action == "login") {
    const phone_number = data.phone_number;

    setUserID(phone_number);
    showChatPage();
    sendRequest({ action: "get_account_details" });
    sendRequest({ action: "get_contacts" });
  } else if (action == "get_account_details") {
    console.log(data);
    const displayname = data.displayname;
    setProfileName(displayname);
  } else if (action == "get_contacts") {
    const contacts = data;
    fillContactBox(contacts, false);
  } else if (action == "get_chat") {
    const messages = data;
    fillMessageBox(messages, false);
  } else if (action == "message") {
    console.log(data);
    document.getElementById("message-input").value = "";
    const message_by = data.send_by;
    if (userMessages.hasOwnProperty(message_by)) {
      userMessages[message_by].push(data);
    } else {
      userMessages[message_by] = [];
      fillContactBox(
        [
          {
            nickname: message_by,
            contact_number: message_by
          },
        ],
        true
      );
    }
    const selected_contact = getSelectedContact();
    const messages = userMessages[selected_contact];
    fillMessageBox(messages, true);
  } else if (action == "add_contact") {
    console.log(data);
    fillContactBox([data], true);
  }
}

function sendRequest(data) {
  socket.send(JSON.stringify(data));
}

function login() {
  const phone_number = document.getElementById("login-phone-number").value;
  const password = document.getElementById("login-password").value;
  const req_body = {
    action: "login",
    phone_number: phone_number,
    password: password,
  };
  sendRequest(req_body);
}

function signup() {
  const phone_number = document.getElementById("signup-phone-number").value;
  const password = document.getElementById("signup-password").value;
  const firstname = document.getElementById("signup-firstname").value;
  const lastname = document.getElementById("signup-lastname").value;
  const displayname = document.getElementById("signup-displayname").value;
  const email = document.getElementById("signup-email").value;

  const req_body = {
    action: "signup",
    phone_number: phone_number,
    firstname: firstname,
    lastname: lastname,
    displayname: displayname,
    email: email,
    password: password,
  };
  sendRequest(req_body);
}

function sendMessage() {
  const messageBox = document.getElementById("message-input");
  const message = messageBox.value;
  // messageBox.value = ""
  const data = {
    action: "message",
    message_text: message,
    sent_to: getSelectedContact(),
  };
  console.log(data);
  // fillMessageBox([data], true)
  sendRequest(data);
}

function showUserChat(contact_number) {
  setSelectedContact(contact_number);
  const data = {
    action: "get_chat",
    contact_number: contact_number,
  };
  console.log(data);
  showMessageInputBox();
  sendRequest(data);
}

function addContact() {
  const contact = document.getElementById("add-contact-phone-number").value;
  const nickname = document.getElementById("add-contact-nickname").value;
  document.getElementById("add-contact-phone-number").value = "";
  document.getElementById("add-contact-nickname").value = "";
  const data = {
    action: "add_contact",
    contact_number: contact,
    nickname: nickname,
  };
  sendRequest(data);
  showChatPage();
  // fillContactBox([data], true);
}
