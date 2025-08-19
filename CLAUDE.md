# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Class Tracker is a Streamlit-based educational data management tool for tracking student performance across multiple areas including homework submission, comments, dictation scores, spelling tests, and grammar errors. The application uses SQLite for data persistence and provides a simple web interface for teachers.

## Commands

### Development
- `streamlit run app.py` - Start the development server
- `pip install -r requirements.txt` - Install dependencies

### Dependencies
Core dependencies are defined in `requirements.txt`:
- streamlit==1.39.0 (web framework)
- pandas==2.2.2 (data manipulation)
- plotly==5.22.0 (data visualization)
- sqlite3 (database - built into Python)
- pydub==0.25.1 (audio processing for dictation)
- datetime (built into Python)

## Architecture

### Database Schema
The application uses SQLite with the following key tables managed in `utils/database.py`:
- `classes` - Class information
- `students` - Student records linked to classes
- `homework` - Daily homework submission tracking (on_time/late/absent)
- `comments` - Student observations categorized by English/UOI/General Behaviour
- `dictation_tasks` - Dictation exercises with audio and transcripts
- `dictation_scores` - Individual student dictation performance
- `spelling_tests` - Weekly spelling test scores out of 20
- `grammar_errors` - Grammar mistakes categorized by error type
- `todos` - Teacher task management

Database path: `database/school.db`

### Application Structure
- `app.py` - Main Streamlit application with navigation
- `utils/database.py` - Database initialization and query utilities
- `pages/` - Individual feature modules loaded via exec():
  - `add_class.py` - Class and student management
  - `homework_tracker.py` - Daily homework submission tracking with calendar view
  - `comments.py` - Student observation logging
  - `dictation.py` - Audio dictation scoring system
  - `spelling_tests.py` - Weekly spelling test tracking
  - `grammar_errors.py` - Grammar mistake categorization
  - `todo.py` - Personal task management

### Key Patterns
- Each page module uses `sys.path.append()` to access utils
- Database operations use the `execute_query()` helper function
- Streamlit forms are used for data entry
- Color-coded displays (green/red/gray) for homework status
- Expandable sections for class/student organization

### Data Flow
1. Teachers create classes and add students via `add_class.py`
2. Daily data entry through individual feature pages
3. Data stored in SQLite database via `utils/database.py`
4. Historical data displayed with pandas DataFrames and styling
5. Summary statistics calculated from database queries

## Important Implementation Notes

- Audio files for dictation are handled through Streamlit file upload
- Homework status uses constrained values: 'on_time', 'late', 'absent'
- Grammar errors are categorized using predefined types for Chinese ESL learners
- Student performance data is aggregated for term-end reporting
- Database initialization occurs automatically on app startup