# Monitor de Ações Brasileiras

## Overview

This is a Brazilian stock market monitoring application built with Streamlit. The application provides real-time tracking of Brazilian stocks (B3 stocks) with features like automatic refresh, watchlist management, and formatted display of financial data. It uses Yahoo Finance as the data source and presents information in a user-friendly dashboard format.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple, modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface providing real-time stock monitoring
- **Data Layer**: Yahoo Finance API integration through yfinance library
- **Business Logic**: Stock data management with caching mechanisms
- **Utilities**: Formatting functions for currency, percentages, and market cap display

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Primary Streamlit application entry point
- **Responsibilities**: 
  - Page configuration and layout management
  - Session state management for watched stocks and auto-refresh settings
  - User interface rendering including sidebar controls
  - Integration with stock data manager and database system

### 2. Stock Database Manager (stock_database.py)
- **Purpose**: Complete database system for Brazilian stock information
- **Key Features**:
  - Persistent JSON storage with comprehensive stock data
  - On-demand database updates with progress tracking
  - Multi-threaded data collection from Yahoo Finance API
  - Search functionality by name, ticker, or industry
  - Sector-based filtering and browsing
  - Database statistics and status monitoring
  - Automatic cache management with 24-hour expiry

### 3. Stock Data Manager (stock_data.py)
- **Purpose**: Handles real-time stock data retrieval and caching
- **Key Features**:
  - Data caching with 30-second expiry to reduce API calls
  - Error handling for failed stock data requests
  - Batch processing of multiple stock tickers
  - Integration with Yahoo Finance API via yfinance library

### 4. Utility Functions (utils.py)
- **Purpose**: Provides formatting functions for financial data display
- **Functions**:
  - Currency formatting with Brazilian Real (R$) notation
  - Percentage formatting for stock changes
  - Market cap formatting with appropriate scaling (K, M, B)
  - Locale-aware formatting with fallback mechanisms

## Data Flow

1. **User Input**: Users can add stock tickers through the sidebar interface
2. **Data Retrieval**: StockDataManager fetches data from Yahoo Finance API
3. **Caching**: Retrieved data is cached for 30 seconds to improve performance
4. **Processing**: Raw financial data is processed and formatted using utility functions
5. **Display**: Formatted data is presented in the Streamlit interface
6. **Auto-Refresh**: Optional automatic updates every 2 seconds for real-time monitoring

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework for the user interface
- **yfinance**: Yahoo Finance API client for stock data retrieval
- **pandas**: Data manipulation and analysis
- **locale**: System locale support for Brazilian Portuguese formatting

### Data Source
- **Yahoo Finance**: Primary data source for Brazilian stock market data (B3 exchange)
- **Stock Format**: Uses .SA suffix for Brazilian stocks (e.g., ITUB4.SA, PETR4.SA)

## Deployment Strategy

The application is designed for Replit deployment with the following characteristics:

- **Runtime**: Python-based Streamlit application
- **Dependencies**: Managed through standard Python package management
- **Configuration**: Streamlit page configuration optimized for wide layout
- **Session Management**: Uses Streamlit's built-in session state for data persistence
- **Performance**: Implements caching to minimize API calls and improve response times

### Default Watchlist
The application comes pre-configured with major Brazilian stocks:
- ITUB4.SA (Itaú Unibanco)
- PETR4.SA (Petrobras)
- VALE3.SA (Vale)
- BBDC4.SA (Bradesco)
- ABEV3.SA (Ambev)

### Complete Stock Database System (Updated: July 2025)
The application now uses a comprehensive database system for Brazilian stocks:
- **Complete B3 stock coverage** with 300+ Brazilian stocks
- **JSON-based persistent storage** with detailed stock information
- **On-demand database updates** via configuration panel button
- **Comprehensive stock data** including:
  - Company names and ticker symbols
  - Industry sectors and classifications
  - ISIN codes for international identification
  - Direct links to market data (dadosdemercado.com.br)
  - Market cap, currency, and exchange information
- **Intelligent caching** with 24-hour expiry for performance
- **Manual update control** - users decide when to refresh data
- **No API call limits** during normal operation
- **Robust error handling** with fallback mechanisms
- **Database statistics** showing total stocks, sectors, and last update

### Key Features
- Real-time stock price monitoring with comprehensive financial metrics
- Automatic refresh capability every 2 seconds
- Dynamic watchlist management with multiple addition methods:
  - Search by name or ticker
  - Browse by sector
  - Quick-add popular stocks
  - Manual ticker entry
- Brazilian currency formatting with smart scaling (K, M, B, T)
- Error handling for unavailable stocks
- Responsive web interface with tabbed navigation
- Database statistics display (total stocks and sectors available)