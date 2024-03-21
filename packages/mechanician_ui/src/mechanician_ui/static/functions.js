      
        function send_prompt(socket) {
            var prompt_text = $('#input').val().trim();
            if (prompt_text) {
                let user_message_container = $('<div class="message-container">');
                user_message_container.append($('<p class="message-header">').html("You"));
                let content_with_breaks = prompt_text.replace(/\n/g, '<br>');
                // var htmlContent = marked.parse(content_with_breaks);
                user_message_container.append($('<p class="message-text">').html(content_with_breaks));
                // user_message_container.append($('<p class="message-text">').html(htmlContent));
                $('#messages').append(user_message_container);
                save_messages_to_local_storage({'from': 'ai'});
                save_messages_to_local_storage({'from': 'user', 'message': prompt_text});
                socket.send(JSON.stringify({data: prompt_text}));
                $('#input').val('');
                adjust_textarea_height_and_change_button_color();
                current_ai_response = null;
                // check_scroll(); // Check scroll after sending a prompt
                setTimeout(check_scroll, 0); // Ensure check_scroll runs after the DOM updates
            }
        }


        function check_session_init_ws() {
            var ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            var socket = new WebSocket(ws_protocol + window.location.host + "/ws");
            var token = localStorage.getItem('jwt_token');
            if (!token) {
                window.location.href = "/login";
            } else {
                // Only initialize WebSocket connection if the session check passes
                init_web_socket(socket);
            }

            document.getElementById('send').addEventListener('click', function() {
                send_prompt(socket);
            });

            document.getElementById('input').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send_prompt(socket);
                }
            });

            document.getElementById('attachment').addEventListener('click', function() {
                document.getElementById('file_input').click(); // Programmatically click the hidden file input
            });

            document.getElementById('file_input').addEventListener('change', function(e) {
                // Ensure a file was selected
                if (this.files && this.files[0]) {
                    var reader = new FileReader();

                    reader.onload = function(e) {
                        // Place the file content into the input field
                        document.getElementById('input').value = e.target.result;
                        adjust_textarea_height_and_change_button_color();
                        send_prompt(socket);
                    };

                    // Read the text file
                    reader.readAsText(this.files[0]);
                }
            });

            return socket;
        }


        function adjust_textarea_height_and_change_button_color() {
            var textarea = document.getElementById('input');
            var send_button = document.getElementById('send');

            // Adjusting the textarea height
            textarea.style.height = 'auto'; // Reset height to auto to get the correct new height
            textarea.style.height = textarea.scrollHeight + 'px'; // Set new height based on scroll height

            // Change the #send button color based on the input
            if (textarea.value.length > 0) {
                // send_button.style.backgroundColor = '#4CAF50'; // Example: Change to a green color when text is entered
                send_button.style.color = '#222'; // Change text color to white for better contrast
                send_button.style.backgroundColor = '#FFF'; 
            } else {
                // send_button.style.backgroundColor = '#222'; // Revert to original color when there's no text
                send_button.style.color = '#222'; // Revert text color to grey
                send_button.style.backgroundColor = '#373737'; // Revert button color
            }
        }


        // Simplified check_scroll function
        function check_scroll() {
            var content_element = document.getElementById('content');
            var scroll_indicator = document.getElementById('scroll_indicator');
            // Logic to determine if scrolling is needed
            var is_scrollable = content_element.scrollHeight > content_element.clientHeight;
            var is_scrolled_to_bottom = content_element.scrollHeight - content_element.scrollTop <= content_element.clientHeight;
            
            // After adding content, scroll to the bottom if the user hasn't manually scrolled up
            if (!user_has_scrolled) {
                var content_element = document.getElementById('content');
                content_element.scrollTop = content_element.scrollHeight;
            }

            // Show or hide the scroll indicator
            scroll_indicator.style.display = is_scrollable && !is_scrolled_to_bottom ? 'block' : 'none';
        }

        function perform_logout() {
            localStorage.removeItem('jwt_token');
            // Make a request to the logout endpoint
            $.ajax({
                type: "POST",
                url: "/logout",
                success: function(data) {
                    // Redirect or update UI on successful logout
                    window.location.href = "/login";
                },
                error: function(response) {
                    // Handle error
                    console.log("Logout failed:", response);
                }
            });
        }

        function init_web_socket(socket) {
            
            socket.onopen = function(e) {
                console.log('Connected to the server.');
                var token = localStorage.getItem('jwt_token');
                // Send the token to the server to authenticate the WebSocket connection
                socket.send(JSON.stringify({token: token}));

                let sys_message_container = $('<div class="message-container">');
                sys_message_container.append($('<p class="message-header">').html("System"));
                current_sys_response = $('<p class="message-text">').text("Connected to AI...");
                sys_message_container.append(current_sys_response);
                $('#messages').append(sys_message_container);
                check_scroll(); // Check scroll after connecting
            };

            socket.onclose = function(e) {
                console.log('Disconnected from the server:', e.reason);
                let sys_message_container = $('<div class="message-container">');
                sys_message_container.append($('<p class="message-header">').html("System"));
                current_sys_response = $('<p class="message-text">').text("Disconnected. Please refresh the page to reconnect.");
                sys_message_container.append(current_sys_response);
                $('#messages').append(sys_message_container);
            };

            socket.onclose = function(e) {
                // Check if the close event was unexpected
                if (!e.wasClean) {
                    console.log('Disconnected from the server:', e.reason);
                    let sys_message_container = $('<div class="message-container">');
                    sys_message_container.append($('<p class="message-header">').html("System"));
                    let current_sys_response = $('<p class="message-text">').text("Disconnected. Attempting to reconnect...");
                    sys_message_container.append(current_sys_response);
                    $('#messages').append(sys_message_container);

                    // Attempt to reconnect after a delay
                    setTimeout(check_session_init_ws, 5000); // Reconnect after 5 seconds
                } else {
                    // Handle intentional disconnection differently, if needed
                    console.log('Disconnected from the server:', e.reason);
                }
            };

            socket.onmessage = function(event) {
                var msg = event.data;
                save_messages_to_local_storage({'from': 'ai', 'message': msg}); // Save each incoming message to local storage
                display_message(msg); // Display the incoming message
            };
        }

        function adjust_input_container_width() {
            const sidebar_width = 260; // Fixed sidebar width
            const minimum_width = 50; // Minimum width of the input-container
            const optimal_width = 675; // Default optimal width of the input-container
            const increased_width = 775; // Increased width of the input-container when there is enough room
            const threshold_width = 935; // Threshold for when to increase the input-container width
            const available_width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0) - sidebar_width - 10; // Calculate the maximum available width

            let adjusted_width;
            if (available_width > threshold_width) {
                adjusted_width = increased_width; // Set width to 775px if there is enough room
            } else {
                adjusted_width = Math.min(Math.max(available_width, minimum_width), optimal_width); // Calculate the adjusted width
            }

            const input_container = document.getElementById('input-container');
            if (input_container) {
                input_container.style.width = `${adjusted_width}px`; // Set the adjusted width to the input-container
            }
        }




        // Function to save messages to local storage
        function save_messages_to_local_storage(message) {
            // Retrieve existing messages from local storage
            let messages = JSON.parse(localStorage.getItem('saved_messages')) || [];
            messages.push(message); // Add new message to the array
            localStorage.setItem('saved_messages', JSON.stringify(messages)); // Save back to local storage
        }

        // Function to load and display messages from local storage
        function load_messages_from_local_storage() {
            let messages = JSON.parse(localStorage.getItem('saved_messages')) || [];
            messages.forEach(function(msg) {
                display_stored_message(msg); // Function to display a message
            });
        }

        // Function to display a message
        function display_message(msg) {
            let content_with_breaks = msg.replace(/\n/g, '<br>');
             // Use marked.js to parse the Markdown
            // var htmlContent = marked.parse(content_with_breaks);
            if (!current_ai_response) {
                let ai_message_container = $('<div class="message-container">');
                ai_message_container.append($('<p class="message-header">').html("AI"));
                current_ai_response = $('<p class="message-text">');
                ai_message_container.append(current_ai_response);
                $('#messages').append(ai_message_container);
            }
            current_ai_response.append(content_with_breaks);
            // current_ai_response.append(htmlContent);
            check_scroll(); // Check scroll after receiving a response
        }

        // Function to display a message
        function display_stored_message(msg) {
            if (msg.from == "ai") {
                if ('message' in msg) {
                    let content_with_breaks = msg.message.replace(/\n/g, '<br>');
                    // var htmlContent = marked.parse(content_with_breaks);
                    if (!current_ai_response) {
                        let ai_message_container = $('<div class="message-container">');
                        ai_message_container.append($('<p class="message-header">').html("AI"));
                        current_ai_response = $('<p class="message-text">');
                        ai_message_container.append(current_ai_response);
                        $('#messages').append(ai_message_container);
                    }
                    current_ai_response.append(content_with_breaks);
                    // current_ai_response.append(htmlContent);
                }
                else {
                    current_ai_response = null;
                    return;
                }
            }
            else if (msg.from == "user") {
                let user_message_container = $('<div class="message-container">');
                user_message_container.append($('<p class="message-header">').html("You"));
                let content_with_breaks = msg.message.replace(/\n/g, '<br>');
                // var htmlContent = marked.parse(content_with_breaks);
                let message_text_p = $('<p class="message-text">').html(content_with_breaks);
                // let message_text_p = $('<p class="message-text">').html(htmlContent);
                user_message_container.append(message_text_p);
                $('#messages').append(user_message_container);
            }
            
            // After adding content, scroll to the bottom if the user hasn't manually scrolled up
            if (!user_has_scrolled) {
                var content_element = document.getElementById('content');
                content_element.scrollTop = content_element.scrollHeight;
            }
            check_scroll(); // Check scroll after receiving a response
        }
