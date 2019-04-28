function setName() {
    const name =document.querySelector('#name').value;
    localStorage.setItem('name', name);
    document.querySelector('#nama').setAttribute("disabled", "disabled"); 
}                          
document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/test');
     
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
            document.querySelector('#task1').value="";
            socket.emit('submit message', {'message': message,'name':name, 'rooma':rooma});
        };

        //should emit a "submit message" event
        document.querySelector('#search').onclick = () => {
            alert("room searched")
            const room = document.querySelector('#room-name').value;           
            socket.emit('search room', {'room':room});
        };
    });
    // When a new message is announced, add to the paragraph
    socket.on('announce message', data => { 
        const p = document.createElement('p');
        p.innerHTML = `<b>${data.name}:</b> ${data.message}`;
        document.querySelector('#message').append(p);
        const small = document.createElement('small');
        document.querySelector('#message').append(small);
        small.innerHTML = `<b>Message Time:</b> ${data.time}`;
        const hr = document.createElement('hr');
        document.querySelector('#message').append(hr);

        shouldScroll = message.scrollTop + message.clientHeight === message.scrollHeight;
        if (!shouldScroll) {
            scrollToBottom();
        }
    });
    // When a  room is announced, add to the paragraph
    socket.on('announce room', data => {
        alert("room announced")
        var i;
        obj = JSON.parse(data);
        for (i = 0; i < obj.room.row.length; i++) {
         const p = document.createElement('p');
        p.innerHTML = `<b>${obj.room.row[i]}</b>`;
        }
        document.querySelector('#roomResults').append(p);
    });

    function scrollToBottom() {
    message.scrollTop = message.scrollHeight;
    }
   
});
