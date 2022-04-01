![Home page](static/home_page.png)

## Project
An anonymous chat application to keep your identity safe.

## Features
- Create new chat rooms.
- Join existing chat rooms. 
- Set your anonymous username.
- Real-time message delivery.
- Chat without creating an account.

## How does flack keep the user anonymous?

* Flack does not store users' communications via chatrooms in Flack's database server and once a message's delivered it'll be disposed of, however, it remains in the owner's session until the owner logged out.
* It lets users choose a nickname due to sake of users' identities.
- [x] Passwords are encrypted
- [x] Nicknames represent users behind their identities.

## Technology Stack Used In This Project
* Python
* Flask
* JavaScript
* Socket Programming
* BootStrap
* JQuery
* HTML/CSS

## Flack Live
### [Click here]( https://flack-web-app.herokuapp.com/) 

## Run This Project on Your Local Machine

1. Clone the repository to your local desktop
    ```
    git clone paste_link_you_copied
    ```
2. Change the directory 
    ```
    cd FlackApp
    ```
3. Install requirements.txt
    ```
    pip install -r requirements.txt 
    ```
4. Run the following command to create a database locally
    ```
    python create.py
    ```
5. Set environment variables in your shell
    ```
    export FLASK_APP=application.py
    ```    
6. Run the application
    ```
    flask run
    ```
 
## How to Contribute

1. Make a Fork.
2. Clone the repository to your local desktop.
    ```
    git clone paste_link_you_copied
    ```
3. Create a new branch (It's necessary).
    ```
    git checkout -b branch-name
    ```
4. Make changes and Add to Staging here.
    ```
    git add.
    ```
5. Commit changes.
    ```
    git commit -m "Message you want to write"
    ```
    * _Always __write the message__ short and easy to understand (ideally 3 to 5 words)._
6. Push the changes so that a pull request will be generated.
    ```
    git push -u origin branchName
    ```
7. Make PR.
8. Commits should be descriptive.
9. Try to minimize conflicts.
10. Follow these steps only after you have Git installed in your system.

## Where to Contribute
1. __UX/UI__
    * You can improve the existing User Interface or can introduce a new layout for Flack.
2. __Code reformat__
    * You can introduce more concise and readable code 
3. __Improvements in Backend__
    * You can find any bug or error and can fix it
4. __Readme file__
    * If you think that something is missing from the readme file. You can introduce new sections for the readme file or can improve the existing one. 


[Click here](https://github.com/HemendraKhatik/FlackApp) to Contribute 



