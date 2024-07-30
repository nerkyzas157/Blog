# Blog

A simple blog website created for learning purposes.

## Features

- User authentication (sign up, log in, log out)
- Create, edit, and delete blog posts
- View all posts and individual post details

## Technologies Used

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS
- **Database**: SQLite (locally), PostgreSQL

## Installation

1. Clone the repository:

```bash
git clone https://github.com/nerkyzas157/Blog.git
cd Blog
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python main.py
```

## Folder Structure

- `static/`: CSS files and other static resources
- `templates/`: HTML templates
- `forms.py`: Form classes for handling user input
- `main.py`: Main application file
- `requirements.txt`: List of dependencies
- `Procfile`: Configuration for deployment on Heroku

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Acknowledgements

- This project was created for learning purposes. Inspired by various online tutorials and Flask documentation.