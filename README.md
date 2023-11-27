# Expense Splitting App

  

## Overview

  

This Expense Splitting App is a FastAPI-based web application that allows users to manage shared expenses and simplify balances among participants.

  

## Features

 

-  **User Management:** Register users with unique email addresses and manage user details.

-  **Expense Creation:** Create expenses with various split types, including EQUAL, EXACT, and PERCENTAGE.

-  **Expense Simplification:** Simplify expenses to generate balanced amounts owed between participants.

  

## Table of Contents

  

- [Installation & Running](#installation)

- [API Endpoints](#api-endpoints)

- [Configuration](#configuration)

  

## Installation & Running

  

1. Clone the repository:
```git clone https://github.com/gseiten/splitwise.git```

2. Install the dependencies
```pip install -r requirements.txt```

3. Change into project directory
```cd splitwise```

4. Run the server
```uvicorn main:app --reload```

### Access the API at http://localhost:8000/docs

  
  

## API Endpoints

### Create User

*Endpoint: POST /users/*
Purpose: This API allows users to register in the system by providing their name, email, and mobile number. It ensures that each user has a unique email address.

  

### Create Expense

*Endpoint: POST /expenses/*
Purpose: Users can use this API to create new expenses with various split types. The split types include "EQUAL" (dividing the expense equally among participants), "EXACT" (specifying exact amounts for each participant), and "PERCENTAGE" (specifying percentages for each participant).


### Simplify Expenses

*Endpoint: POST /simplify-expenses/*
Purpose: This API is designed to simplify expenses for a particular user. It calculates the net amounts owed or to be received by the user from other participants in all their expenses. The simplified balances help in settling debts efficiently.


###  Configuration

-   `DATABASE_URL`: Database connection URL.
-   `SENDGRID_API_KEY`: API key for SendGrid email service.
-   `SMTP_SERVER`: SMTP server for sending emails.
-   `SMTP_PORT`: SMTP server port.
-   `SMTP_USERNAME`: SMTP username.
-   `SMTP_PASSWORD`: SMTP password.
-   `EMAIL_SENDER`: Default sender email address.
