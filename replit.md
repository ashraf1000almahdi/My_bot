# Telegram Video Downloader Bot

## Overview

This is a comprehensive Telegram bot application that allows users to download videos from various platforms. The system consists of a Flask web application for administration and a Telegram bot for user interaction. The bot requires users to subscribe to a specific channel before accessing download features and includes Arabic language support.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Flask Web Application**: Provides an admin dashboard for monitoring users, downloads, and statistics
- **Telegram Bot**: Handles user interactions and video download requests
- **Database Layer**: Uses SQLAlchemy with SQLite for data persistence
- **Video Processing**: Integrates with yt-dlp for video extraction and downloading

## Key Components

### Backend Components

1. **Flask Application (`app.py`)**
   - Configures the main Flask application
   - Sets up SQLAlchemy database connection
   - Handles middleware configuration with ProxyFix
   - Manages application context and model initialization

2. **Telegram Bot (`bot.py`)**
   - Implements the TelegramBot class with handlers for commands and messages
   - Manages user interactions including subscription verification
   - Handles video download requests and status updates

3. **Database Models (`models.py`)**
   - User model: Stores user information and subscription status
   - Download model: Tracks download requests and their status
   - Relationships between users and their downloads

4. **Configuration (`config.py`)**
   - Centralized configuration management
   - Bot settings, channel requirements, and download limits
   - Arabic language message templates

### Service Components

1. **Subscription Checker (`subscription_checker.py`)**
   - Verifies user subscription to required Telegram channel
   - Handles Telegram API interactions for membership verification

2. **Video Downloader (`video_downloader.py`)**
   - Integrates with yt-dlp for video information extraction
   - Handles video format and quality selection
   - Manages download file size limitations

3. **Web Routes (`routes.py`)**
   - Dashboard route for admin statistics
   - User management endpoints
   - Download history and monitoring

### Frontend Components

1. **Dashboard Interface (`templates/dashboard.html`)**
   - Real-time statistics display
   - User activity monitoring
   - Download analytics with charts

2. **User Management (`templates/users.html`)**
   - User listing and filtering
   - Subscription status management
   - Export functionality

3. **Download Management (`templates/downloads.html`)**
   - Download history tracking
   - Status filtering and monitoring
   - Bulk operations support

## Data Flow

1. **User Registration**: Users start the bot and are registered in the database
2. **Subscription Verification**: Bot checks if user is subscribed to required channel
3. **Video Request**: User sends video URL to bot
4. **Processing**: Bot extracts video information and downloads content
5. **Delivery**: Bot sends downloaded video back to user
6. **Tracking**: All activities are logged in the database for admin monitoring

## External Dependencies

- **Telegram Bot API**: For bot functionality and user interactions
- **yt-dlp**: For video extraction and downloading from multiple platforms
- **Flask**: Web framework for admin dashboard
- **SQLAlchemy**: ORM for database operations
- **Bootstrap**: Frontend styling framework
- **Chart.js**: For dashboard analytics visualization

## Deployment Strategy

The application is designed to run on Replit with the following setup:

1. **Dual Thread Architecture**: Flask web server and Telegram bot run in separate threads
2. **Environment Variables**: Bot token and database URL configured via environment variables
3. **Static File Serving**: CSS and JavaScript files served through Flask
4. **Database Initialization**: Tables created automatically on application startup
5. **Logging**: Comprehensive logging for debugging and monitoring

The main entry point (`main.py`) starts both the Flask web server and Telegram bot simultaneously, allowing for real-time monitoring while the bot serves users.

## Bot Information

- **Bot Name**: Download VideoSaver pro
- **Bot Username**: @DownloadProVideoSaver_bot
- **Bot ID**: 8160949585
- **Channel**: @hackrs98
- **Admin ID**: 7024930860
- **Developer**: المهندس/اشرف المهدي
- **Contact**: @A_H_a_h_a_h_a_hn

## Features Implemented

### Core Bot Features
- **Subscription Verification**: Mandatory subscription to @hackrs98 channel
- **Video Download**: Support for YouTube, Instagram, TikTok, Twitter, Facebook, and more
- **Daily Limits**: 10 downloads per user per day
- **Arabic Interface**: Complete Arabic language support with RTL layout
- **User Management**: Database tracking of users and their download history
- **Error Handling**: Comprehensive error messages and retry mechanisms

### Web Dashboard Features
- **Real-time Statistics**: Live dashboard with user counts and download metrics
- **User Management**: View, filter, and manage bot users
- **Download Monitoring**: Track all downloads with status and platform information
- **Arabic Interface**: Professional RTL Arabic web interface
- **Charts & Analytics**: Visual representation of daily downloads and success rates
- **Export Functionality**: Data export capabilities for users and downloads

### Technical Implementation
- **Flask Web Application**: Professional admin dashboard on port 5000
- **PostgreSQL Database**: Scalable database with proper relationships
- **Simple HTTP Bot**: Custom Telegram bot implementation using HTTP API
- **Video Processing**: yt-dlp integration for multi-platform video downloads
- **Professional UI**: Bootstrap dark theme with Arabic RTL support
- **Security**: Environment variable management for sensitive data

## Changelog

- July 05, 2025: Complete professional Telegram video downloader bot system implemented
  - Telegram bot with subscription verification and video download capabilities
  - Professional web dashboard with Arabic RTL interface
  - PostgreSQL database with user and download tracking
  - Multi-platform video download support
  - Daily download limits and comprehensive error handling

## User Preferences

Preferred communication style: Simple, everyday language.