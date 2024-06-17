<h1 align="center">
  <br>
    <img src="assets/tourid.png" alt="TourID" width="200">
  <br>
    TourID
  <br>
   <p><em>One Click, Many Destination</em></p>
</h1>

## Table of Contents
- [Architecture](#architecture)
- [Development](#development)
- [Deployment](#deployment)
  - [Firebase](#firebase)
  - [Cloud Storage](#cloud-storage)
  - [Secret Manager](#secret-manager)
  - [Service Account](#service-account)
  - [Cloud Run](#cloud-run)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentations)
- [Cloud Computing Team](#cloud-computing-team)

## Architecture

## Development
- Clone this repository
```
git clone https://github.com/TourID/Cloud-Computing
```

- Create virtual environment folder
```
python -m venv your_venv_folder
```

- Activate your virtual environment
  <br>
  Windows:
  ```
  .\your_venv_folder\Scripts\activate
  ```
  MacOS/Linux:
  ```
  source your_venv_folder/bin/activate

- Install dependencies
```
pip install -r requirements.txt
```
- Run the app
```
python3 app.py
```

## Deployment

### Cloud Storage
- Create a bucket
  - Default class: Standard
  - Enforce public access prevention
  - Uniform access control enabled
- The required outcomes is `BUCKET_NAME`

### Secret Manager
- Add secrets for your credentials
  <br>
  Refer to the image below for an example:
  <br>
![Secret Manager](assets/secret-manager.png)

### Service Account
- Create 2 new service accounts
  - Cloud Run
    - Cloud Run Invoker role
  - TourID Cloud Run Services
    - Cloud Datastore User
    - Cloud Datastore Viewer
    - Custom Storage Object Creator
    - Firestore Service Agent
    - Secret Manager Secret Accessor
    <br>
  Refer to the image below for an example
![Service Account](assets/service-acc-1.png)
![Service Account](assets/service-acc-2.png)
