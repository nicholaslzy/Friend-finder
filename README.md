# Friend Finder

Link to my youtube demonstration:  
https://www.youtube.com/watch?v=LdI79-OHYDo


## This is my final project for CS50x
Similar to Week9's Finance problem set, I used Flask, a web framework written in python. I used SQLite3 to store and retrieve
information about new and existing users. The website is written in HTML and CSS, and javascript functions were created to
allow for the 'Add Friend' as well as 'Accept' and 'Decline' buttons.

The main page of my website, the Find Friends page, auto populates by retrieving information from 2 SQLite3 tables, namely a
users_info table (which stores information about each user) as well as the friend_requests table. This allows a 'pending' button
to show instead of the 'add friend' button to show for users which the current user has already sent a friend request to.

    ```
    if request.method == "GET":
        user_list = db.execute(
            "SELECT users_info.*, friend_requests.status FROM users_info "
            "LEFT JOIN friend_requests ON ((users_info.user_id = friend_requests.receiver_id AND friend_requests.sender_id = ?) "
            "OR (users_info.user_id = friend_requests.sender_id AND friend_requests.receiver_id = ?)) "
            "WHERE users_info.user_id != ? AND (friend_requests.status IS NULL OR friend_requests.status = 'pending')",
            user_id, user_id, user_id
        )
        print(user_list)
        return render_template("findfriends.html", user_list=user_list)
        ```

## AJAX
I also made use of AJAX (Asynchronous Javascript and XML) to implement my 'Add Friend' button, which would change to read 'pending' when clicked. This ensures a smoother website experience as the webpage would not need to refresh each time the button is clicked.

        ```
        function handleAddFriendClick(button) {
            button.disabled = true; // Disable the button to prevent multiple clicks
            button.textContent = 'Pending'; // Change the button text to 'Pending'

            var friendId = button.getAttribute('data-friend-id');

            // Send an AJAX POST request
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/findfriends', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        // Handle success, optionally update UI further based on response
                    } else {
                        // Handle error, revert button state
                        button.disabled = false;
                        button.textContent = 'Add friend';
                    }
                }
            };

            // Send the request with the friend_id parameter
            xhr.send('friend_id=' + encodeURIComponent(friendId));
        }
        ```
## Homepage
The homepage, also acts as a page that displays all of the current user's friends. It does this by again, retrieving information
from 2 tables, the users_info table and the relationships table. It first checks to see the relationship between users and the
current user, before displaying information about their friends.

    ```
    @app.route("/", methods=["GET", "POST"])
    @login_required
    def homepage():
        user_id = session["user_id"]
        if request.method == "GET":
            friends = db.execute(
                "SELECT u.* "
                "FROM users_info u "
                "JOIN relationships r ON (u.user_id = r.friend_id AND r.user_id = ?) "
                "OR (u.user_id = r.user_id AND r.friend_id = ?)",
                user_id, user_id
            )
            print(friends)
            return render_template("index.html", friends=friends)


        {% for user in friends %}
            <tr>
                <td>{{ user['name'] }}</td>
                <td>{{ user['age'] }}</td>
                <td>{{ user['gender'] }}</td>
                <td>{{ user['school'] }}</td>
                <td>{{ user['course'] }}</td>
            </tr>
        {% endfor %}
    ```

I thoroughly enjoyed my time in this course, I think Professor David and the rest of the CS50
course staff did an amazing job in making this course as enjoyable and informational as it was!
I would recommend this course to anyone interested in pursuing CS in college. Thank you.

## About CS50
CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.
