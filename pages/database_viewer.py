import streamlit as st
import sys
import os
import pandas as pd
import sqlite3

# Import from parent directory
try:
    from utils.database import execute_query, get_connection
    from utils.auth import is_james
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.database import execute_query, get_connection
    from utils.auth import is_james

# SECURITY: Only James can access this page
if not is_james():
    st.error("🔒 Access Denied - James Only")
    st.stop()

st.header("🗄️ Database Viewer")
st.warning("⚠️ **JAMES ONLY** - This page shows the complete database structure and data")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Database Relationships", "Tables & Schema", "Raw Data", "SQL Query", "Database Stats"])

with tab1:
    st.subheader("🔗 Database Relationships & Structure")
    
    st.write("### 📊 How Data is Connected")
    
    # Visual relationship diagram
    st.write("""
    ```
    USERS (Teachers/Admins)
    ├── id (Primary Key)
    ├── username, password_hash, full_name, role
    └── Links to: classes.teacher_id, students.teacher_id
    
    CLASSES (Teacher's Classes)
    ├── id (Primary Key)
    ├── name, teacher_id (→ users.id)
    └── Links to: students.class_name
    
    STUDENTS (Individual Students)
    ├── id (Primary Key) 
    ├── name, class_name, teacher_id (→ users.id)
    └── Links to: homework.student_id, comments.student_id, 
                  essay_marks.student_id, dictation_scores.student_id,
                  spelling_tests.student_id, grammar_errors.student_id
    
    ASSESSMENT TABLES (All link to students.id):
    ├── homework (daily submission tracking)
    ├── comments (teacher observations)
    ├── essay_marks (essay scores & feedback)
    ├── dictation_scores (listening test results)
    ├── spelling_tests (weekly spelling scores)
    └── grammar_errors (error tracking)
    ```
    """)
    
    # Show actual foreign key relationships
    st.write("### 🔑 Foreign Key Relationships")
    
    relationships = [
        ("classes", "teacher_id", "users", "id", "Each class belongs to one teacher"),
        ("students", "teacher_id", "users", "id", "Each student belongs to one teacher"),
        ("homework", "student_id", "students", "id", "Each homework entry for one student"),
        ("comments", "student_id", "students", "id", "Each comment about one student"),
        ("essay_marks", "student_id", "students", "id", "Each essay score for one student"),
        ("dictation_scores", "student_id", "students", "id", "Each dictation score for one student"),
        ("dictation_scores", "task_id", "dictation_tasks", "id", "Each score for one dictation task"),
        ("spelling_tests", "student_id", "students", "id", "Each spelling test for one student"),
        ("grammar_errors", "student_id", "students", "id", "Each grammar error for one student"),
    ]
    
    relationship_df = pd.DataFrame(relationships, columns=[
        "From Table", "Foreign Key", "To Table", "Primary Key", "Relationship"
    ])
    st.dataframe(relationship_df, use_container_width=True)
    
    # Show data flow example
    st.write("### 📈 Data Flow Example")
    st.info("""
    **Example: How a teacher's data flows through the system**
    
    1. **Teacher logs in** → `users` table (james, id=8)
    2. **Creates a class** → `classes` table (name="Year 4A", teacher_id=8)
    3. **Adds students** → `students` table (name="Alice", class_name="Year 4A", teacher_id=8)
    4. **Records homework** → `homework` table (student_id=Alice's ID, status="on_time")
    5. **Writes comments** → `comments` table (student_id=Alice's ID, comment="Great work!")
    6. **Marks essays** → `essay_marks` table (student_id=Alice's ID, score=85)
    
    **Key Point:** All student data is isolated by teacher_id - teachers only see their own data!
    """)
    
    # Show current data counts by relationship
    st.write("### 📊 Current Data Distribution")
    
    try:
        # Get teacher data counts
        teacher_stats = execute_query("""
            SELECT 
                u.username,
                u.full_name,
                COUNT(DISTINCT c.id) as classes,
                COUNT(DISTINCT s.id) as students,
                COUNT(DISTINCT h.id) as homework_entries,
                COUNT(DISTINCT cm.id) as comments,
                COUNT(DISTINCT em.id) as essays,
                COUNT(DISTINCT ds.id) as dictations,
                COUNT(DISTINCT st.id) as spelling_tests,
                COUNT(DISTINCT ge.id) as grammar_errors
            FROM users u
            LEFT JOIN classes c ON u.id = c.teacher_id
            LEFT JOIN students s ON u.id = s.teacher_id
            LEFT JOIN homework h ON s.id = h.student_id
            LEFT JOIN comments cm ON s.id = cm.student_id
            LEFT JOIN essay_marks em ON s.id = em.student_id
            LEFT JOIN dictation_scores ds ON s.id = ds.student_id
            LEFT JOIN spelling_tests st ON s.id = st.student_id
            LEFT JOIN grammar_errors ge ON s.id = ge.student_id
            WHERE u.role IN ('teacher', 'admin')
            GROUP BY u.id, u.username, u.full_name
            ORDER BY u.username
        """)
        
        if teacher_stats:
            stats_df = pd.DataFrame(teacher_stats, columns=[
                'Username', 'Full Name', 'Classes', 'Students', 'Homework', 
                'Comments', 'Essays', 'Dictations', 'Spelling', 'Grammar'
            ])
            st.dataframe(stats_df, use_container_width=True)
            
            # Visual chart
            numeric_cols = ['Classes', 'Students', 'Homework', 'Comments', 'Essays', 'Dictations', 'Spelling', 'Grammar']
            chart_data = stats_df.set_index('Username')[numeric_cols]
            st.bar_chart(chart_data)
        else:
            st.info("No teacher data found yet")
            
    except Exception as e:
        st.error(f"Error loading relationship data: {str(e)}")

with tab2:
    st.subheader("📋 Database Schema")
    
    # Get all tables
    try:
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        
        if tables and len(tables) > 0:
            st.write("**Database Tables:**")
            for table in tables:
                try:
                    table_name = table[0] if isinstance(table, (list, tuple)) else str(table)
                    
                    with st.expander(f"📊 Table: {table_name}"):
                        # Get table schema
                        schema = execute_query(f"PRAGMA table_info({table_name})")
                        if schema:
                            schema_df = pd.DataFrame(schema, columns=['ID', 'Name', 'Type', 'NotNull', 'Default', 'PK'])
                            st.dataframe(schema_df, use_container_width=True)
                        
                        # Get row count
                        count_result = execute_query(f"SELECT COUNT(*) FROM {table_name}")
                        count = count_result[0][0] if count_result else 0
                        st.write(f"**Row Count:** {count}")
                        
                        # Show sample data (first 5 rows)
                        if count > 0:
                            sample_data = execute_query(f"SELECT * FROM {table_name} LIMIT 5")
                            if sample_data:
                                columns = [col[1] for col in schema] if schema else []
                                if columns:
                                    sample_df = pd.DataFrame(sample_data, columns=columns)
                                    st.write("**Sample Data (first 5 rows):**")
                                    st.dataframe(sample_df, use_container_width=True)
                except Exception as table_error:
                    st.error(f"Error loading table {table_name}: {str(table_error)}")
        else:
            st.info("No tables found in database")
    except Exception as e:
        st.error(f"Error loading database schema: {str(e)}")

with tab3:
    st.subheader("📄 Raw Data Viewer")
    
    # Table selector
    try:
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        if tables:
            table_names = [table[0] if isinstance(table, (list, tuple)) else str(table) for table in tables]
            selected_table = st.selectbox("Select Table to View:", table_names)
        
            if selected_table:
                # Pagination
                page_size = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)
                
                # Get total count
                count_result = execute_query(f"SELECT COUNT(*) FROM {selected_table}")
                total_rows = count_result[0][0] if count_result else 0
                total_pages = (total_rows - 1) // page_size + 1 if total_rows > 0 else 1
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1) - 1
                
                # Get data for current page
                offset = page * page_size
                data = execute_query(f"SELECT * FROM {selected_table} LIMIT {page_size} OFFSET {offset}")
                
                if data:
                    # Get column names
                    schema = execute_query(f"PRAGMA table_info({selected_table})")
                    columns = [col[1] for col in schema] if schema else []
                    
                    if columns:
                        df = pd.DataFrame(data, columns=columns)
                        st.dataframe(df, use_container_width=True)
                        
                        st.write(f"Showing rows {offset + 1}-{min(offset + page_size, total_rows)} of {total_rows}")
                        
                        # Download as CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download {selected_table} as CSV",
                            data=csv,
                            file_name=f"{selected_table}_export.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Could not get column information for this table")
                else:
                    st.info(f"No data in table '{selected_table}'")
        else:
            st.info("No tables available")
    except Exception as e:
        st.error(f"Error in raw data viewer: {str(e)}")

with tab4:
    st.subheader("🔍 Custom SQL Query")
    st.warning("⚠️ **BE CAREFUL** - Only use SELECT statements. Write operations could break the app!")
    
    # SQL Query editor
    query = st.text_area(
        "SQL Query:", 
        value="SELECT name FROM sqlite_master WHERE type='table';",
        height=150,
        help="Enter your SQL query here. Only SELECT statements recommended."
    )
    
    if st.button("🚀 Execute Query"):
        if query.strip():
            try:
                # Basic safety check
                query_upper = query.upper().strip()
                if not query_upper.startswith('SELECT'):
                    st.error("❌ Only SELECT queries are allowed for safety!")
                else:
                    results = execute_query(query)
                    if results:
                        # Try to create DataFrame
                        try:
                            df = pd.DataFrame(results)
                            st.dataframe(df, use_container_width=True)
                            st.success(f"✅ Query executed successfully! ({len(results)} rows)")
                            
                            # Download results
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                        except:
                            # Fallback for queries that don't return tabular data
                            st.write("**Results:**")
                            for row in results:
                                st.write(row)
                    else:
                        st.info("Query executed but returned no results")
            except Exception as e:
                st.error(f"❌ Query Error: {str(e)}")
        else:
            st.error("❌ Please enter a query")

with tab5:
    st.subheader("📈 Database Statistics")
    
    # Database file info
    try:
        import os
        db_path = "database/school.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            st.metric("Database Size", f"{db_size / 1024:.1f} KB")
        
        # Connection info
        conn = get_connection()
        st.success("✅ Database connection healthy")
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Database issues: {str(e)}")
    
    # Table sizes
    st.write("**Table Row Counts:**")
    if tables:
        table_stats = []
        for table in tables:
            table_name = table[0]
            count = execute_query(f"SELECT COUNT(*) FROM {table_name}")[0][0]
            table_stats.append({'Table': table_name, 'Rows': count})
        
        stats_df = pd.DataFrame(table_stats)
        st.dataframe(stats_df, use_container_width=True)
        
        # Visual chart
        if len(stats_df) > 0:
            st.bar_chart(stats_df.set_index('Table')['Rows'])
    
    # Recent activity
    st.write("**Recent User Activity:**")
    recent_users = execute_query("""
        SELECT username, full_name, role, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    if recent_users:
        users_df = pd.DataFrame(recent_users, columns=['Username', 'Full Name', 'Role', 'Created'])
        st.dataframe(users_df, use_container_width=True)

# Footer warning
st.markdown("---")
st.error("""
🚨 **SECURITY REMINDER**
- This page is ONLY visible to James
- Joe and Jake cannot access the database viewer
- It will NOT be accessible to teachers or anyone who clones the repo
- Keep James credentials secure
- All other users can only see their own data
""")