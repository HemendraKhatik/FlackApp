function setName() {
    const name =document.querySelector('#name').value;
    localStorage.setItem('name', name);
    document.querySelector('#nama').setAttribute("disabled", "disabled"); 
}                            
document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
     
    // When connected
    socket.on('connect', () => {   
        //checking local storage valiable           
        if (!localStorage.getItem('name'))
            localStorage.setItem('name','Anonymous'); 
        //should emit a "submit message" event
        document.querySelector('#send').onclick = () => {
            name = localStorage.getItem('name');
            const message = document.querySelector('#task1').value;
            const rooma = document.querySelector('#room').innerHTML;
            socket.emit('submit message', {'message': message,'name':name, 'rooma':rooma});
        };
    });
    // When a new message is announced, add to the paragraph
    socket.on('announce message', data => { 
        const p = document.createElement('p');
        p.innerHTML = `${data.name}: ${data.message}`;
        document.querySelector('#message').append(p);
        const small = document.createElement('small');
        document.querySelector('#message').append(small);
        small.innerHTML = `message time: 5:10pm`;
        const hr = document.createElement('hr');
        document.querySelector('#message').append(hr);

        shouldScroll = message.scrollTop + message.clientHeight === message.scrollHeight;
        if (!shouldScroll) {
            scrollToBottom();
        }
    });
    function scrollToBottom() {
    message.scrollTop = message.scrollHeight;
    }
   
});