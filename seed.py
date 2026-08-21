import os
from datetime import datetime, date, timedelta
from app import create_app
from models import db, User, Project, Document, Inspection, Category, Defect, Comment, ActivityLog, Notification

def seed_database():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        # 1. Create Predefined Categories
        categories_data = [
            ("Functional Defect", "Logical error or missing functional design element"),
            ("Design Error", "Flaw in structural or procedural design rationale"),
            ("Architecture Issue", "Violation of architectural pattern or component coupling"),
            ("Interface Issue", "API signature or system interface mismatch"),
            ("Database Issue", "Schema inconsistency, missing keys, or normalization error"),
            ("Security Issue", "Vulnerability, unencrypted flow, or authentication flaw"),
            ("Performance Issue", "Bottleneck, unoptimized payload, or resource leak"),
            ("Usability Issue", "Poor UX design, confusing navigation, or workflow flaw"),
            ("Requirement Mismatch", "Design does not satisfy functional requirements"),
            ("Documentation Error", "Incorrect descriptions, outdated references, or typos"),
            ("Missing Information", "Incomplete specification or missing section"),
            ("Inconsistency", "Contradictory information between modules or diagrams"),
            ("Standards Violation", "Non-conformance to team coding or design guidelines"),
            ("Cosmetic Issue", "Formatting, naming, or presentation typo in specification")
        ]

        category_objs = {}
        for name, desc in categories_data:
            cat = Category(name=name, description=desc, is_custom=False)
            db.session.add(cat)
            category_objs[name] = cat

        db.session.commit()
        print("Defect categories seeded.")

        # 2. Create Users across Roles
        # Passwords for all demo accounts: 'password123'
        admin = User(
            name="Alex Rivera",
            email="admin@designinspect.com",
            username="admin",
            role="Admin",
            status="Active"
        )
        admin.set_password("password123")

        pm = User(
            name="Sarah Jenkins",
            email="pm@designinspect.com",
            username="sjenkins",
            role="Project Manager",
            status="Active"
        )
        pm.set_password("password123")

        reviewer = User(
            name="Rahul Sharma",
            email="reviewer@designinspect.com",
            username="rsharma",
            role="Reviewer",
            status="Active"
        )
        reviewer.set_password("password123")

        developer = User(
            name="Amit Patel",
            email="dev@designinspect.com",
            username="apatel",
            role="Developer",
            status="Active"
        )
        developer.set_password("password123")

        reviewer2 = User(
            name="Elena Rostova",
            email="elena@designinspect.com",
            username="erostova",
            role="Reviewer",
            status="Active"
        )
        reviewer2.set_password("password123")

        db.session.add_all([admin, pm, reviewer, developer, reviewer2])
        db.session.commit()
        print("Users seeded.")

        # 3. Create Sample Project: Online Banking System
        proj = Project(
            project_code="PRJ-101",
            name="Online Banking System",
            description="Core enterprise banking portal overhaul including multi-factor auth, microservices architecture, transaction processing engine, and open banking REST APIs.",
            manager_id=pm.id,
            status="Active",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 11, 30),
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        db.session.add(proj)
        db.session.commit()

        # Secondary demo project
        proj2 = Project(
            project_code="PRJ-102",
            name="Healthcare Mobile Telehealth Platform",
            description="HIPAA-compliant telemedicine iOS/Android design specification including video triage, patient EHR integration, and biometric authentication.",
            manager_id=pm.id,
            status="Under Review",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 12, 15),
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        db.session.add(proj2)
        db.session.commit()
        print("Projects seeded.")

        # 4. Create Design Documents for Online Banking System
        doc1 = Document(
            doc_code="DOC-201",
            project_id=proj.id,
            name="Software Architecture Document",
            document_type="Software Architecture Document",
            version="v2.0",
            author_id=admin.id,
            reviewer_id=reviewer.id,
            review_status="Approved",
            size_metric_type="Pages",
            size_metric_value=52.0,
            upload_date=datetime.utcnow() - timedelta(days=45)
        )

        doc2 = Document(
            doc_code="DOC-202",
            project_id=proj.id,
            name="Database Design Specification",
            document_type="Database Design",
            version="v1.2",
            author_id=developer.id,
            reviewer_id=reviewer.id,
            review_status="Revision Required",
            size_metric_type="Pages",
            size_metric_value=38.0,
            upload_date=datetime.utcnow() - timedelta(days=25)
        )

        doc3 = Document(
            doc_code="DOC-203",
            project_id=proj.id,
            name="API Design Specification",
            document_type="API Design",
            version="v1.5",
            author_id=developer.id,
            reviewer_id=reviewer2.id,
            review_status="In Review",
            size_metric_type="Pages",
            size_metric_value=30.0,
            upload_date=datetime.utcnow() - timedelta(days=15)
        )

        db.session.add_all([doc1, doc2, doc3])
        db.session.commit()
        print("Design Documents seeded.")

        # 5. Create Inspections
        insp1 = Inspection(
            inspection_code="INS-001",
            project_id=proj.id,
            document_id=doc1.id,
            document_version="v2.0",
            inspection_type="Architecture Review",
            lead_reviewer_id=reviewer.id,
            review_team="Rahul Sharma, Elena Rostova, Sarah Jenkins",
            inspection_date=date(2026, 8, 10),
            status="Completed",
            summary="Comprehensive architecture evaluation of microservices topology and caching strategy. Identified minor bottleneck risks in JWT session validation."
        )

        insp2 = Inspection(
            inspection_code="INS-002",
            project_id=proj.id,
            document_id=doc2.id,
            document_version="v1.2",
            inspection_type="Formal Design Inspection",
            lead_reviewer_id=reviewer.id,
            review_team="Rahul Sharma, Amit Patel",
            inspection_date=date(2026, 8, 20),
            status="In Progress",
            summary="Detailed walkthrough of relational ER diagrams, transaction isolation levels, and foreign key indexes."
        )

        db.session.add_all([insp1, insp2])
        db.session.commit()
        print("Inspections seeded.")

        # 6. Create Defects (DEF-001 through DEF-006)
        def1 = Defect(
            defect_code="DEF-001",
            inspection_id=insp2.id,
            document_id=doc2.id,
            document_version="v1.2",
            project_id=proj.id,
            title="Database relationship inconsistency in Account-Transaction entity mapping",
            description="The ER diagram on Page 14 depicts a 1-to-1 relationship between Account and Transaction entities, whereas the functional requirements specify a 1-to-Many relationship.",
            category_id=category_objs["Database Issue"].id,
            severity="High",
            priority="High",
            status="In Progress",
            location="Database Schemas",
            page_section="Page 14, Section 3.2",
            reported_by_id=reviewer.id,
            assigned_to_id=developer.id,
            recommended_fix="Update ER diagram to specify 1-to-N cardinality with cascade delete behavior on account archiving.",
            reviewer_comments="Must be corrected before DB migration script generation.",
            developer_comments="Currently updating the ERD and script templates.",
            due_date=date(2026, 9, 2),
            created_at=datetime.utcnow() - timedelta(days=7),
            updated_at=datetime.utcnow() - timedelta(days=2)
        )

        def2 = Defect(
            defect_code="DEF-002",
            inspection_id=insp2.id,
            document_id=doc3.id,
            document_version="v1.5",
            project_id=proj.id,
            title="Missing authentication validation in public wire transfer API payload",
            description="The wire transfer endpoint specification allows unauthenticated request headers to trigger processing without validating bearer JWT tokens.",
            category_id=category_objs["Security Issue"].id,
            severity="Critical",
            priority="Urgent",
            status="New",
            location="API Spec / Auth Gateway",
            page_section="Page 8, Section 2.1",
            reported_by_id=reviewer.id,
            assigned_to_id=developer.id,
            recommended_fix="Enforce strict AuthMiddleware interceptor and define token authorization schemas in OpenAPI spec.",
            reviewer_comments="Critical vulnerability. Block release until resolved.",
            due_date=date(2026, 8, 30),
            created_at=datetime.utcnow() - timedelta(days=5),
            updated_at=datetime.utcnow() - timedelta(days=5)
        )

        def3 = Defect(
            defect_code="DEF-003",
            inspection_id=insp1.id,
            document_id=doc3.id,
            document_version="v1.5",
            project_id=proj.id,
            title="Incorrect API response structure for failed login attempts",
            description="The REST response payload returns HTTP status 200 OK with error body instead of standard RFC 7807 problem details and HTTP 401/403 status codes.",
            category_id=category_objs["Interface Issue"].id,
            severity="Medium",
            priority="Medium",
            status="Resolved",
            location="Authentication API",
            page_section="Page 19, Section 4.5",
            reported_by_id=reviewer2.id,
            assigned_to_id=developer.id,
            recommended_fix="Align error responses with global API standard RFC 7807.",
            reviewer_comments="Pending reviewer re-verification.",
            developer_comments="Updated the API payload specs to return HTTP 401 with standard JSON error body.",
            due_date=date(2026, 8, 28),
            created_at=datetime.utcnow() - timedelta(days=12),
            updated_at=datetime.utcnow() - timedelta(days=1),
            resolved_at=datetime.utcnow() - timedelta(days=1)
        )

        def4 = Defect(
            defect_code="DEF-004",
            inspection_id=insp1.id,
            document_id=doc1.id,
            document_version="v2.0",
            project_id=proj.id,
            title="High memory consumption during peak payload serialization in reporting module",
            description="Architecture document specifies in-memory buffering for 100K JSON export rows without streaming support, risking OOM crashes on microservice instances.",
            category_id=category_objs["Performance Issue"].id,
            severity="Critical",
            priority="Urgent",
            status="Under Verification",
            location="Reporting Engine Architecture",
            page_section="Page 41, Section 7.4",
            reported_by_id=reviewer.id,
            assigned_to_id=developer.id,
            recommended_fix="Specify server-sent chunked streaming response or async batch worker execution.",
            developer_comments="Refactored reporting spec to use Redis task queue with SSE streaming.",
            due_date=date(2026, 8, 29),
            created_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow() - timedelta(hours=12),
            resolved_at=datetime.utcnow() - timedelta(hours=12)
        )

        def5 = Defect(
            defect_code="DEF-005",
            inspection_id=insp1.id,
            document_id=doc1.id,
            document_version="v2.0",
            project_id=proj.id,
            title="Missing error handling for timeout during OAuth 2.0 handshake",
            description="The sequence diagram does not account for gateway timeout responses from external identity providers.",
            category_id=category_objs["Architecture Issue"].id,
            severity="High",
            priority="High",
            status="Closed",
            location="OAuth Sequence Diagram",
            page_section="Page 22, Section 4.2",
            reported_by_id=reviewer.id,
            assigned_to_id=developer.id,
            recommended_fix="Add fallback retry strategy and timeout exception path to sequence diagram.",
            reviewer_comments="Verified. Added retry circuit breaker pattern.",
            developer_comments="Updated sequence diagram with circuit breaker state transitions.",
            due_date=date(2026, 8, 20),
            created_at=datetime.utcnow() - timedelta(days=20),
            updated_at=datetime.utcnow() - timedelta(days=3),
            resolved_at=datetime.utcnow() - timedelta(days=4),
            closed_at=datetime.utcnow() - timedelta(days=3)
        )

        def6 = Defect(
            defect_code="DEF-006",
            inspection_id=insp2.id,
            document_id=doc2.id,
            document_version="v1.2",
            project_id=proj.id,
            title="Typos in API endpoint parameter names in section 4.1",
            description="Parameter 'usr_acc_num' is misspelled as 'usr_acct_numb' in two sub-tables.",
            category_id=category_objs["Cosmetic Issue"].id,
            severity="Cosmetic",
            priority="Low",
            status="Closed",
            location="Data Dictionary",
            page_section="Page 7, Section 1.3",
            reported_by_id=reviewer2.id,
            assigned_to_id=developer.id,
            recommended_fix="Correct spelling in data dictionary tables.",
            developer_comments="Fixed typo across document.",
            due_date=date(2026, 8, 25),
            created_at=datetime.utcnow() - timedelta(days=15),
            updated_at=datetime.utcnow() - timedelta(days=5),
            resolved_at=datetime.utcnow() - timedelta(days=6),
            closed_at=datetime.utcnow() - timedelta(days=5)
        )

        db.session.add_all([def1, def2, def3, def4, def5, def6])
        db.session.commit()
        print("Defects seeded.")

        # 7. Add Activity Logs for timeline
        logs = [
            ActivityLog(defect_id=def1.id, user_id=reviewer.id, action="Defect Created", old_value=None, new_value="New", timestamp=datetime.utcnow() - timedelta(days=7)),
            ActivityLog(defect_id=def1.id, user_id=reviewer.id, action="Assigned to Developer", old_value="Unassigned", new_value="Amit Patel", timestamp=datetime.utcnow() - timedelta(days=6)),
            ActivityLog(defect_id=def1.id, user_id=developer.id, action="Status Changed", old_value="Assigned", new_value="In Progress", timestamp=datetime.utcnow() - timedelta(days=2)),

            ActivityLog(defect_id=def3.id, user_id=reviewer2.id, action="Defect Created", old_value=None, new_value="New", timestamp=datetime.utcnow() - timedelta(days=12)),
            ActivityLog(defect_id=def3.id, user_id=developer.id, action="Status Changed", old_value="In Progress", new_value="Resolved", timestamp=datetime.utcnow() - timedelta(days=1)),

            ActivityLog(defect_id=def5.id, user_id=reviewer.id, action="Defect Created", old_value=None, new_value="New", timestamp=datetime.utcnow() - timedelta(days=20)),
            ActivityLog(defect_id=def5.id, user_id=developer.id, action="Status Changed", old_value="In Progress", new_value="Resolved", timestamp=datetime.utcnow() - timedelta(days=4)),
            ActivityLog(defect_id=def5.id, user_id=reviewer.id, action="Reviewer Verified", old_value="Under Verification", new_value="Closed", timestamp=datetime.utcnow() - timedelta(days=3))
        ]
        db.session.add_all(logs)

        # 8. Add Comments
        comments = [
            Comment(defect_id=def1.id, user_id=reviewer.id, comment_text="The database relationship is inconsistent with the architecture specification. Please check section 3.2.", created_at=datetime.utcnow() - timedelta(days=6)),
            Comment(defect_id=def1.id, user_id=developer.id, comment_text="Updated the relationship and revised the ER diagram draft.", created_at=datetime.utcnow() - timedelta(days=2)),
            Comment(defect_id=def5.id, user_id=reviewer.id, comment_text="Verified fix in document revision v2.0. Issue resolved.", created_at=datetime.utcnow() - timedelta(days=3))
        ]
        db.session.add_all(comments)

        # 9. Add Notifications
        notifications = [
            Notification(user_id=developer.id, message="You were assigned critical defect DEF-002 (Missing authentication validation)", notification_type="assignment", link=f"/defects/{def2.id}", is_read=False),
            Notification(user_id=reviewer.id, message="Developer Amit Patel marked DEF-004 as Resolved (Pending Verification)", notification_type="status_change", link=f"/defects/{def4.id}", is_read=False),
            Notification(user_id=developer.id, message="Comment added on DEF-001 by Rahul Sharma", notification_type="comment", link=f"/defects/{def1.id}", is_read=True)
        ]
        db.session.add_all(notifications)

        db.session.commit()
        print("Activity logs, comments, and notifications seeded.")
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
