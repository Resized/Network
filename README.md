# Social Network

[![Build Status](https://travis-ci.org/resized/network.svg?branch=master)](https://travis-ci.org/resized/network)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Social Network Single-Page-Application

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)

## Project Overview

The Single-Page-Application Social Network project is a web application social networking platform using JavaScript and Django.

## Features

- User Registration and Authentication: Users can create accounts and log in securely to access the social network.
- Posts/Follow Feed: Users can share posts with other users and see posts on their feed from all/followed users. 
- Likes: Users are able to like/unlike posts on their feed.
- Following System: Allowing users to follow and unfollow other users, customizing their follow feed.
- User Profiles: Each user has a personalized profile page displaying their posts, followers, following, and user-specific information.
- Edit Posts: Users can edit posts they have posted.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/resized/network.git
```

2. Change into the project directory:

```bash
cd your-project/
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

On Windows:

```bash
venv\Scripts\activate
```

On macOS and Linux:

```bash
source venv/bin/activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

6. Apply database migrations:

```bash
python manage.py migrate
```

7. Create a superuser:

```bash
python manage.py createsuperuser
```

8. Run the development server:

```bash
python manage.py runserver
```

The project should now be accessible at `http://127.0.0.1:8000/`.

