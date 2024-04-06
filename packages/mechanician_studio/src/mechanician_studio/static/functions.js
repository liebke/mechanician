      
        var generating_text = false;
        var new_connection = false;

        function send_prompt(socket, username, ai_name, conversation_id) {
            var prompt_text = $('#input').val().trim();
            if (prompt_text) {
                let user_message_container = $('<div class="message-container">');
                user_message_container.append($('<p class="message-header">').html("You"));
                let content_with_breaks = prompt_text.replace(/\n/g, '<br>');
                user_message_container.append($('<p class="message-text">').html(content_with_breaks));
                $('#messages').append(user_message_container);
                if (new_connection) {
                    socket.send(JSON.stringify({data: prompt_text, 
                                                type: 'prompt', 
                                                ai_name: ai_name,
                                                conversation_id: conversation_id}));
                    new_connection = false;
                }
                else {
                    socket.send(JSON.stringify({data: prompt_text,
                                                ai_name: ai_name,
                                                conversation_id: conversation_id,
                                                type: 'prompt'}));
                }
                $('#input').val('');
                adjust_textarea_height_and_change_button_color();
                current_ai_response = null;
                setTimeout(check_scroll, 0); // Ensure check_scroll runs after the DOM updates
            }
        }


        function check_session_init_ws(username, ai_name) {
            var ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            var socket = new WebSocket(ws_protocol + window.location.host + "/ws");
            var token = localStorage.getItem('jwt_token');
            if (!token) {
                window.location.href = "/login";
            } else {
                // Only initialize WebSocket connection if the session check passes
                init_web_socket(socket, username, ai_name);
            }

            document.getElementById('send').addEventListener('click', function() {
                send_prompt(socket, username, get_ai_name(), get_conversation_id());
            });

            document.getElementById('input').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send_prompt(socket, username, get_ai_name(), get_conversation_id());
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
                        send_prompt(socket, username, get_ai_name(), get_conversation_id());
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
                send_button.style.color = '#222'; // Change text color to white for better contrast
                send_button.style.backgroundColor = '#FFF'; 
            } else {
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

        function transform_stop_to_send(socket) {
            if (!generating_text) {
                return;
            }
            generating_text = false;

            // Find the stop button by its new ID
            var stop_button = document.getElementById('send');
            
            // If the stop button exists, transform it back into the send button
            if (stop_button) {
                // Restore the button's ID, class attributes, and inner HTML to match the original send button
                stop_button.className = ''; // Set this to the original class of the send button if it had any
                stop_button.setAttribute('aria-label', 'send prompt'); // Remove the aria-label or set it to the original if needed
                
                // Restore the inner HTML to the SVG of the send button
                stop_button.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="text-white dark:text-black">
                        <path d="M7 11L12 6L17 11M12 18V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                    </svg>
                `;
                
                // Re-attach the original event listener for the send functionality
                stop_button.removeEventListener('click', function() {stop_generating(socket); }); 
                stop_button.addEventListener('click', function() {send_prompt(socket, username, get_ai_name(), get_conversation_id()); }); 
            }
        }
        
        function stop_generating(socket) {
                // Your function to send a stop message over the websocket
                console.log("Stop generating");
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({type: 'stop', ai_name: get_ai_name(), conversation_id: get_conversation_id()})); // Example message format
                }
        }
        

        function transform_send_to_stop(socket) {
            if (generating_text) {
                return;
            }
            generating_text = true;
            setTimeout(function() {transform_stop_to_send(socket); }, 2000); // Revert to the send button after 2 seconds (example delay
            // Find the send button by its ID
            var send_button = document.getElementById('send');
            
            // If the send button exists, transform it into the stop button
            if (send_button) {
                // Update the inner HTML to the SVG of the stop button
                send_button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" height="20" width="20">
                    <!-- Decrease the radius by 1 to account for the increased stroke width -->
                    <circle cx="8" cy="8" r="7" stroke="white" stroke-width="2" fill="none"/>
                    <!-- Adjusted square size and position -->
                    <rect x="4.5" y="4.5" width="7" height="7" fill="white" rx="1"/>
                </svg>
                `;
                send_button.removeEventListener('click', function() {send_prompt(socket, username, get_ai_name(), get_conversation_id()); }); 
                send_button.addEventListener('click',function() {stop_generating(socket);});
            }
        }
        

        function generate_ai_name_select_options(ai_names, defaultValue) {
            const selectElement = document.getElementById('ai_name');
            selectElement.innerHTML = ''; // Clear existing options if any
            
            ai_names.forEach(name => {
                const optionElement = document.createElement('option');
                optionElement.value = name;
                optionElement.textContent = name;
                // Check if the current name is the default value
                if(name === defaultValue) {
                    optionElement.selected = true;
                }
                selectElement.appendChild(optionElement);
            });
        }

        
        function init_web_socket(socket, username) {
            console.log('Initializing WebSocket connection...');
            
            socket.onopen = function(e) {
                console.log('Connected to the server.');
                new_connection = true;
                var token = localStorage.getItem('jwt_token');
                // Send the token to the server to authenticate the WebSocket connection
                socket.send(JSON.stringify({token: token, ai_name: get_ai_name(), conversation_id: get_conversation_id(), type: 'token'}));

                let sys_message_container = $('<div class="message-container">');
                sys_message_container.append($('<p class="message-header">').html("System"));
                current_sys_response = $('<p class="message-text">').text("Connected to " + get_ai_name() + "...");
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

            // Modify your onmessage function to call transform_send_to_stop
            socket.onmessage = function(event) {
                var msg = event.data;
                // save_messages_to_local_storage({'role': 'assistant', 'content': msg}, username, get_ai_name()); // Save each incoming message to local storage
                display_message(msg); // Display the incoming message
                transform_send_to_stop(socket); // Transform the send button into the stop button
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


        // function convert_to_keyword(input_string) {
        //     return input_string.toLowerCase().replace(/\s+/g, '_');
        // }

        // function get_local_storage_key(username, ai_name) {
        //     let ai_name_kw = convert_to_keyword(ai_name);
        //     return username ? `${username}_${ai_name_kw}_saved_messages` : 'saved_messages';
        // }

        // Function to save messages to local storage
        // function save_messages_to_local_storage(message, username, ai_name) {
        //     // Retrieve existing messages from local storage
        //     const storage_key = get_local_storage_key(username, ai_name);
        //     let messages = JSON.parse(localStorage.getItem(storage_key)) || [];
        //     messages.push(message); // Add new message to the array
        //     localStorage.setItem(storage_key, JSON.stringify(messages)); // Save back to local storage
        // }

        function clear_messages_display() {
            $('#messages').empty();
        }

        // Function to load and display messages from local storage
        // function load_messages_from_local_storage(username, ai_name) {
        //     const storage_key = get_local_storage_key(username, ai_name);
        //     let messages = JSON.parse(localStorage.getItem(storage_key)) || [];
        //     messages.forEach(function(msg) {
        //         display_stored_message(msg); // Function to display a message
        //     });
        // }


        function load_conversation_history(username, ai_name, conversation_id) {
            // Get the conversation history from the server /conversation_history endpoint
            $.ajax({
                type: "GET",
                url: "/conversation_history",
                data: {username: username, ai_name: ai_name, conversation_id: conversation_id},
                success: function(data) {
                    // Load the conversation history into the chat window
                    if (data.conversation_history) {
                        data.conversation_history.forEach(function(msg) {
                            display_stored_message(msg); // Function to display a message
                        });
                    }
                },
                error: function(response) {
                    // Handle error
                    console.log("Failed to load conversation history:", response);
                }
            });
        }


        function get_ai_name() {
            return document.getElementById('ai_name').value;
        }


        function get_conversation_id() {
            return document.getElementById('conversation_id').value;
        }

        // Function to display a message
        function display_message(msg) {
            let content_with_breaks = msg.replace(/\n/g, '<br>');
            if (!current_ai_response) {
                let ai_message_container = $('<div class="message-container">');
                ai_message_container.append($('<p class="message-header">').html("AI"));
                current_ai_response = $('<p class="message-text">');
                ai_message_container.append(current_ai_response);
                $('#messages').append(ai_message_container);
            }
            current_ai_response.append(content_with_breaks);
            check_scroll(); // Check scroll after receiving a response
        }

        function list_ai_tools(username, ai_name) {
            // Create a new Promise
            return new Promise(function(resolve, reject) {
                // Get the conversation IDs from the server /list_conversations endpoint
                $.ajax({
                    type: "GET",
                    url: "/list_ai_tools",
                    data: {ai_name: ai_name},
                    success: function(data) {
                        // Resolve the Promise with the data
                        resolve(data);
                    },
                    error: function(response) {
                        // Reject the Promise with the error
                        reject("Failed to list AI Tools: " + response);
                    }
                });
            });
        }

        function list_conversations(username, ai_name) {
            // Create a new Promise
            return new Promise(function(resolve, reject) {
                // Get the conversation IDs from the server /list_conversations endpoint
                $.ajax({
                    type: "GET",
                    url: "/list_conversations",
                    data: {username: username, ai_name: ai_name},
                    success: function(data) {
                        // Resolve the Promise with the data
                        resolve(data);
                    },
                    error: function(response) {
                        // Reject the Promise with the error
                        reject("Failed to list conversation IDs: " + response);
                    }
                });
            });
        }

        function set_conversation_id(conversation_id) {
            document.getElementById('conversation_id').value = conversation_id;
        }

        // Function to display a message
        function display_stored_message(msg) {
            if (msg.role == "assistant") {
                if ('content' in msg) {
                    let content_with_breaks = msg.content.replace(/\n/g, '<br>');
                    let ai_message_container = $('<div class="message-container">');
                    ai_message_container.append($('<p class="message-header">').html("AI"));
                    current_ai_response = $('<p class="message-text">');
                    ai_message_container.append(current_ai_response);
                    $('#messages').append(ai_message_container);
                    current_ai_response.append(content_with_breaks);
                }
                else {
                    current_ai_response = null;
                    return;
                }
            }
            else if (msg.role == "user") {
                let user_message_container = $('<div class="message-container">');
                user_message_container.append($('<p class="message-header">').html("You"));
                let content_with_breaks = msg.content.replace(/\n/g, '<br>');
                let message_text_p = $('<p class="message-text">').html(content_with_breaks);
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
