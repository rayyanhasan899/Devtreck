# Devtreck — Software Requirements Specification

**Product:** Devtreck  
**Document type:** Functional and non-functional requirements  
**Version:** 1.0  
**Status:** Initial requirements baseline

## 1. Product Overview

Devtreck is a personalized task-management and productivity application that combines a traditional to-do list with daily task streaks, progress tracking, and motivation features. Each user has a private account and their own tasks, settings, streaks, statistics, and achievements.

The application should make it easy to capture tasks, organize work, decide what to do next, complete tasks on time, and build consistent habits. Its defining feature is a per-task streak that grows when the user completes a recurring daily task on consecutive calendar days.

### 1.1 Product Goals

- Let users securely create and manage their own accounts.
- Provide complete task CRUD (Create, Read, Update, Delete) functionality.
- Keep each user's information private and separate from every other user's information.
- Make task completion and daily progress quick to understand.
- Track consecutive daily completions for eligible tasks.
- Provide useful productivity features beyond a basic to-do list.
- Make progress visible through statistics, milestones, and achievements.

### 1.2 Intended Platforms

- Responsive web application for desktop, tablet, and mobile browsers.
- The architecture should allow a future mobile application to reuse the same backend API.

### 1.3 Terminology

| Term | Definition |
|---|---|
| Task | An item of work the user intends to complete. |
| One-time task | A task intended to be completed once. |
| Daily task / habit | A task intended to be completed once on each applicable calendar day. |
| Completion | The recorded event that a task was done. |
| Streak | The number of consecutive eligible days on which a daily task was completed. |
| Current streak | The consecutive-day count ending on the most recent qualifying completion, subject to the streak rules below. |
| Best streak | The highest streak count ever achieved for that task. |
| User-local day | A calendar day calculated using the time zone configured in the user's profile. |

## 2. Scope and Assumptions

### 2.1 Included in the Initial Product

- Account registration, login, logout, profile viewing/editing, and account deletion.
- Private, user-owned task management.
- Task details, priorities, due dates, statuses, filters, search, and sorting.
- Daily recurring tasks and per-task streak tracking.
- Dashboard, daily planning, progress statistics, and achievements.
- The additional productivity features described in Section 8.
- Input validation, security controls, error handling, and responsive interface behavior.

### 2.2 Product Rules and Assumptions

1. All application data is owned by an authenticated user unless it is explicitly public in a future release.
2. One-time tasks do **not** build a daily streak. Streaks apply to tasks configured as daily recurring tasks/habits.
3. A daily task can be completed at most once per user-local calendar day for streak purposes. Repeated clicks or duplicate requests must not increase the streak more than once for the same day.
4. A daily task is considered on time for a day when it is marked complete before the next local midnight. A completion at or after the next midnight belongs to the new local day; it cannot retroactively satisfy the previous day.
5. The user's configured time zone determines day boundaries. Daylight-saving changes, where applicable, must be handled using a time-zone-aware date library or equivalent reliable mechanism.
6. Deleting a task removes it from active task lists. Any retained historical data must follow the data-retention and account-deletion policy; the initial product may delete the task's associated history permanently.
7. A task can be edited after creation. Changes that could affect historical streak calculations must not silently rewrite past completion records.
8. The initial version uses a user-configured time zone and does not depend on a user's device being online at midnight.

## 3. User Roles and Permissions

### 3.1 Standard User

A standard user can:

- Register, log in, log out, and manage their own profile.
- Create, view, edit, complete, reopen where permitted, and delete their own tasks.
- View and manage their own daily tasks, streaks, focus sessions, achievements, and statistics.
- Change personal preferences such as time zone, theme, and notification settings.

### 3.2 Administrator

An administrator role is **not required for the initial release**. If administrative tools are introduced later, they must not expose user passwords or permit casual access to private task content.

## 4. Functional Requirements: Accounts and Authentication

### 4.1 Registration

- **ACC-01:** The system shall allow a new user to create an account using a name, email address, and password.
- **ACC-02:** The system shall require a valid email format and a password that meets the configured password policy.
- **ACC-03:** The system shall reject registration when the email address is already registered, using a clear and safe error message.
- **ACC-04:** The system shall trim unnecessary whitespace from appropriate text fields and normalize email addresses consistently before checking uniqueness.
- **ACC-05:** The system shall securely hash passwords before storing them. Plain-text passwords shall never be stored or logged.
- **ACC-06:** The system shall validate registration data on both the client and server.
- **ACC-07:** After successful registration, the system shall either sign the user in or direct them to the login screen, according to the implemented flow.

### 4.2 Login and Logout

- **ACC-08:** The system shall allow users to log in using their registered email and password.
- **ACC-09:** The system shall verify credentials securely and return a generic error for invalid credentials without disclosing whether an email exists.
- **ACC-10:** The system shall establish an authenticated session using a secure session or token mechanism.
- **ACC-11:** Protected screens and API routes shall require valid authentication.
- **ACC-12:** The system shall allow a user to log out and invalidate or remove the applicable client session credentials.
- **ACC-13:** Expired, invalid, or malformed authentication credentials shall be rejected and the user shall be prompted to authenticate again when appropriate.
- **ACC-14:** The authentication implementation shall use environment variables for secrets and shall not commit secrets to source control.

### 4.3 Account Read, Update, and Delete

- **ACC-15:** The user shall be able to view their profile, including name, email, time zone, and selected preferences.
- **ACC-16:** The user shall be able to update permitted profile fields, such as name, time zone, theme, and notification preferences.
- **ACC-17:** A change to the email address shall be validated and shall not conflict with another account. Email verification may be required if email delivery is implemented.
- **ACC-18:** The user shall be able to change their password after providing the required current-password or re-authentication proof.
- **ACC-19:** The user shall be able to request account deletion after an explicit confirmation step.
- **ACC-20:** Account deletion shall delete or irreversibly anonymize the user's personal data, tasks, completion history, and associated records according to the application's stated retention policy.
- **ACC-21:** Users shall not be able to read or modify another user's account or profile by changing an ID in a request.

### 4.4 Optional Account Recovery

- **ACC-22:** If password-reset email delivery is configured, users shall be able to request a time-limited, single-use password-reset link.
- **ACC-23:** The system shall avoid revealing whether an account exists when a password-reset request is submitted.

## 5. Functional Requirements: Task Management (CRUD)

### 5.1 Task Data

Each task shall support the following fields, as applicable:

- Unique task ID.
- Owner/user ID.
- Title (required).
- Description (optional).
- Status: `pending`, `in-progress`, or `completed`.
- Task type: `one-time` or `daily`.
- Priority: `low`, `medium`, or `high`.
- Due date and optional due time.
- Optional category or tag(s).
- Creation timestamp and last-updated timestamp.
- Completion timestamp or separate completion-history records.
- Optional estimated duration.
- Optional reminder configuration.
- Optional ordering/rank for manual list arrangement.

### 5.2 Create Tasks

- **TSK-01:** An authenticated user shall be able to create a task.
- **TSK-02:** A task shall require a non-empty title within a documented maximum length.
- **TSK-03:** The user shall be able to add an optional description, priority, task type, due date/time, category, estimated duration, and reminder.
- **TSK-04:** A new task shall default to `pending` unless the product interface defines another explicit default.
- **TSK-05:** New tasks shall be associated with the currently authenticated user on the server. The server shall not trust a client-supplied owner ID.
- **TSK-06:** A daily task shall be eligible for streak tracking according to Section 7.
- **TSK-07:** The system shall display a success state after a task is created and update the task list without requiring an unnecessary full-page reload.

### 5.3 Read and View Tasks

- **TSK-08:** A user shall be able to view all of their active tasks.
- **TSK-09:** A user shall be able to view the details of an individual task.
- **TSK-10:** A user shall be able to view completed tasks and completion history through a completed/history view.
- **TSK-11:** Task queries shall return only records belonging to the authenticated user.
- **TSK-12:** The system shall show useful empty states when a user has no tasks or no results match the selected filters.

### 5.4 Update Tasks

- **TSK-13:** A user shall be able to edit the title and description of their tasks.
- **TSK-14:** A user shall be able to update priority, task type, due date/time, category/tags, estimated duration, reminder, and status where applicable.
- **TSK-15:** The system shall validate updates on the server and preserve existing values when optional fields are omitted from a partial update.
- **TSK-16:** The system shall update the task's modification timestamp after a successful edit.
- **TSK-17:** Changing a one-time task into a daily task shall initialize streak tracking without inventing prior completions.
- **TSK-18:** Changing a daily task into a one-time task shall stop future streak tracking while retaining or handling historical records according to the product's documented rules.
- **TSK-19:** Editing a task's schedule or recurrence settings shall not silently rewrite previously recorded completion dates.

### 5.5 Complete, Reopen, and Delete Tasks

- **TSK-20:** A user shall be able to mark a pending or in-progress task as completed.
- **TSK-21:** The system shall record the completion time using a trusted server timestamp.
- **TSK-22:** Completing a one-time task shall mark it completed and remove it from the default active-task view.
- **TSK-23:** Completing a daily task shall create a completion record for the applicable user-local day and update its streak if the day has not already been counted.
- **TSK-24:** The interface shall provide a clear way to reopen a task if reopening is supported. Reopening a task shall not silently erase a legitimate historical completion record.
- **TSK-25:** A user shall be able to delete their own task after an intentional action; irreversible deletion should have a confirmation or an undo option.
- **TSK-26:** Deleting a task shall not delete or affect another user's records.
- **TSK-27:** The server shall reject duplicate completion submissions for the same task and user-local day for streak purposes.

### 5.6 Search, Filters, and Sorting

- **TSK-28:** Users shall be able to search tasks by title and, where practical, description.
- **TSK-29:** Users shall be able to filter by status, task type, priority, category/tag, due date, and overdue state.
- **TSK-30:** Users shall be able to sort by due date, priority, creation date, updated date, and title.
- **TSK-31:** Users shall be able to switch between useful views such as All, Today, Upcoming, Overdue, Daily Tasks, and Completed.
- **TSK-32:** Search, filtering, and sorting shall operate only on the current user's authorized task set.

## 6. Task Rules and Lifecycle

### 6.1 Status Definitions

- `pending`: created but not yet started or completed.
- `in-progress`: work has started but is not complete.
- `completed`: the task has been marked complete.

The interface may provide a simpler one-click completion action while retaining these statuses internally.

### 6.2 Due Dates and Overdue Tasks

- A task with a due date in the past and no qualifying completion shall be identified as overdue.
- Tasks without due dates shall not be labelled overdue.
- Daily recurring tasks should be shown in the daily view on each applicable day, even after being completed for that day, so the user can see today's completion state and streak.
- A daily task may have an optional target time, but its streak deadline is the end of the applicable user-local calendar day unless a future version explicitly supports a different rule.

### 6.3 Categories and Tags

- Users shall be able to assign a task to an optional category, such as Study, Work, Personal, Health, or Projects.
- Users shall be able to create, rename, and delete their own custom categories if custom categories are included in the initial interface.
- Deleting a category shall not unexpectedly delete the tasks previously assigned to it; those tasks should become uncategorized or prompt the user to reassign them.

## 7. Daily Streak System

### 7.1 Eligibility and Completion Rules

- **STR-01:** Only tasks configured as daily recurring tasks shall have a streak.
- **STR-02:** A daily task shall have a streak counter, best streak, and completion history.
- **STR-03:** A qualifying completion shall count for the user's local calendar day, determined by the user's configured time zone.
- **STR-04:** The user must complete the daily task before the next local midnight to receive credit for that day. For example, a task due for October 2 must be completed before the start of October 3 in the user's time zone.
- **STR-05:** A task shall count at most one completion per local calendar day. Multiple completions or duplicate requests on one day shall not raise the streak more than once.
- **STR-06:** If a task is completed on the next consecutive calendar day, its current streak shall increase by one.
- **STR-07:** If a task misses an eligible calendar day, its current streak shall reset according to the streak definition. The best streak shall remain unchanged.
- **STR-08:** The system shall show the current streak and best streak for every eligible task.
- **STR-09:** The system shall show the most recent qualifying completion date and whether today's task has been completed.
- **STR-10:** Streak calculations shall be based on completion-history records and reliable timestamps, not merely on a client-side counter.
- **STR-11:** Concurrent or repeated requests shall not create duplicate daily completion records or inconsistent streak totals.

### 7.2 Starting a Streak

To avoid ambiguous behavior, the initial product shall use this rule:

1. Creating a daily task initializes its current streak to `0` and best streak to `0`.
2. The first qualifying completion establishes a streak of `1` for that day.
3. Completing the task on the next consecutive calendar day increases the current streak to `2`, and so on.
4. Creating a daily task does not itself count as a completion.

### 7.3 Missed Days and Streak Display

- If yesterday was an eligible day and the task was not completed yesterday, the task shall show that the streak has ended or reset; its best streak remains available.
- The interface shall distinguish a streak that is active for today from a streak that ended after a missed day.
- A task should display a clear call to action when today's completion is still pending.
- The app shall not grant completion credit retroactively unless a future, explicitly defined recovery feature permits it.

### 7.4 Streak Edge Cases

- **New task created today:** The streak remains `0` until the task is completed; the first completion makes it `1`.
- **Task completed twice today:** Count one completion day only.
- **Task completed after midnight:** Credit the new local day, not the previous one.
- **User changes time zone:** Recalculate future day boundaries using the new time zone but preserve stored completion timestamps and historical completion-day information. The interface should communicate that changing time zones may affect which local day is current.
- **Task is paused or deleted:** Pausing and deleting must not create fake completion credit. Deletion follows the data policy in Section 2.2.
- **Clock or client time is incorrect:** Use server-generated timestamps and the configured time zone, not the device clock alone.

### 7.5 Optional Streak Protection

- **STR-12 (Optional):** The product may offer a limited Streak Freeze that protects a missed day. If implemented, the allowance, eligibility, and effect on the streak must be clearly displayed and applied consistently.
- **STR-13 (Optional):** Users must not be able to repeatedly exploit freeze or recovery actions to produce unlimited streak credit. Any use should be recorded in the task's history.

Streak Freeze is an optional enhancement and must not be assumed to exist in the first release.

## 8. Stand-Out Productivity Features

The following features extend Devtreck beyond a basic to-do list. Features 8.1–8.5 are recommended product features; implementation may be phased, but each included feature must meet its listed requirements.

### 8.1 Smart Daily Plan

A personalized view that helps users decide what to work on today.

- **PLN-01:** Provide a Today view containing tasks due today, overdue tasks, and daily tasks not yet completed today.
- **PLN-02:** Allow users to mark a small number of tasks as their top priorities for the day.
- **PLN-03:** Offer a suggested order based on due date, priority, overdue status, and estimated duration.
- **PLN-04:** Explain or make visible why a task is suggested, such as “high priority” or “due today.”
- **PLN-05:** Let the user override the suggested order. The application shall assist the user rather than force a plan.
- **PLN-06:** If estimated durations are present, display an approximate total planned workload for the day.

### 8.2 Focus Timer and Focus Sessions

A built-in focus tool for working on one task without distractions.

- **FOC-01:** Users shall be able to start a focus session associated with a task or with a general focus activity.
- **FOC-02:** Provide a configurable work timer and break timer. A standard preset such as 25 minutes of focus and 5 minutes of break may be offered.
- **FOC-03:** Allow a user to pause, resume, or stop a session.
- **FOC-04:** Record session start, end, duration, associated task, and completion state.
- **FOC-05:** Display daily and weekly focus time in the user's statistics.
- **FOC-06:** A timer ending shall not automatically mark its associated task complete.
- **FOC-07:** Timer state should remain understandable if the user navigates to another screen or refreshes the page. The backend should record session events where necessary to avoid relying entirely on a running browser timer.

### 8.3 XP, Levels, and Achievements

A lightweight reward system that recognizes consistent work without making the application dependent on competition.

- **ACH-01:** Award XP for valid task completions and completed focus sessions using clearly defined, configurable rules.
- **ACH-02:** Avoid awarding duplicate XP for duplicate requests or repeatedly toggling a task between complete and incomplete.
- **ACH-03:** Provide levels based on accumulated XP and show the user's current level and progress to the next level.
- **ACH-04:** Provide achievements or badges for milestones, such as completing the first task, reaching a streak milestone, finishing a number of tasks, or accumulating focus time.
- **ACH-05:** Show the reason and date when an achievement is earned.
- **ACH-06:** Recompute or validate rewards on the server so users cannot grant themselves arbitrary XP by altering client requests.
- **ACH-07:** Reward rules shall be transparent and shall not encourage users to create meaningless duplicate tasks merely to gain points.

### 8.4 Weekly Insights and Progress Analytics

A summary that helps users understand productivity patterns.

- **INS-01:** Show tasks completed today and over the last 7 days.
- **INS-02:** Show task completion rate for a clearly specified period and define the calculation used.
- **INS-03:** Show current and best streaks, total daily-task completions, and streak milestones.
- **INS-04:** Show total focus time and session count for the selected period when focus sessions are enabled.
- **INS-05:** Show completion trends by day and, where categories exist, by category.
- **INS-06:** Distinguish actual recorded data from estimates and avoid presenting insufficient data as a meaningful trend.
- **INS-07:** All analytics shall be scoped to the signed-in user.

### 8.5 Task Notes, Checklists, and Subtasks

Allow a large task to be broken into smaller, actionable steps.

- **SUB-01:** Users may add checklist items or subtasks to a parent task.
- **SUB-02:** Each checklist item shall have a title and completion state.
- **SUB-03:** Users shall be able to add, edit, reorder, complete, and delete checklist items they own through the parent task.
- **SUB-04:** Display checklist progress, such as “3 of 5 complete,” on the task card or detail view.
- **SUB-05:** Completing all checklist items shall not automatically complete the parent task unless that behavior is explicitly enabled and communicated.
- **SUB-06:** Subtasks shall inherit access control from their parent task and shall not be accessible independently to another user.

### 8.6 Optional Reminders and Notifications

- **NOT-01 (Optional):** Users may configure reminders for tasks with due dates or for daily tasks.
- **NOT-02 (Optional):** Reminders shall respect the user's time zone and notification preferences.
- **NOT-03 (Optional):** Users shall be able to enable or disable each supported notification channel.
- **NOT-04 (Optional):** If push or email delivery is not configured, the application shall not imply that an external notification was sent; in-app reminders may be used instead.
- **NOT-05 (Optional):** Notifications should avoid sending repeated or duplicate reminders for the same task occurrence.

## 9. Dashboard and User Interface Requirements

- **UI-01:** The dashboard shall show a summary of today's tasks, completed tasks, outstanding tasks, and daily streaks.
- **UI-02:** The primary task list shall make task title, status, priority, due date, and daily streak easy to scan.
- **UI-03:** Daily tasks shall visibly indicate whether they have been completed today and show their current streak.
- **UI-04:** Provide clear, consistent actions for adding a task, editing a task, marking it complete, and deleting it.
- **UI-05:** Use confirmation or undo behavior for destructive actions.
- **UI-06:** Provide loading, success, empty, and error states for asynchronous operations.
- **UI-07:** Prevent accidental multiple submissions by disabling or guarding actions while a request is in progress, without relying on the interface as the only duplicate protection.
- **UI-08:** Forms shall identify required fields and explain validation errors near the relevant input.
- **UI-09:** The interface shall be responsive at common desktop, tablet, and mobile viewport sizes.
- **UI-10:** Provide keyboard-accessible navigation and visible focus states for interactive controls.
- **UI-11:** Use sufficient color contrast and do not communicate task status, priority, or streak state through color alone.
- **UI-12:** Dates and times shall be displayed consistently using the user's chosen time zone.
- **UI-13:** Provide a settings screen for profile, time zone, theme, and applicable notification preferences.

## 10. Suggested Screens and Navigation

1. **Landing / Welcome:** Brief product introduction and entry points to sign up or log in.
2. **Registration:** Account creation form and validation feedback.
3. **Login:** Secure sign-in form and optional password recovery.
4. **Dashboard / Today:** Daily plan, priority tasks, today's streaks, and short progress summary.
5. **All Tasks:** Searchable, filterable, sortable list of active tasks.
6. **Task Details / Editor:** Task fields, due date, category, subtasks, completion history, and streak details where applicable.
7. **Daily Tasks / Streaks:** Daily habits with today's completion status, current streak, and best streak.
8. **Focus:** Focus timer and session history.
9. **Progress / Achievements:** XP, levels, badges, weekly insights, and progress charts.
10. **Settings / Profile:** Profile details, time zone, theme, notification settings, password change, and account deletion.

## 11. Data and Entity Requirements

The following entities are a suggested logical model. Actual schemas may differ, provided all requirements and ownership rules are satisfied.

### 11.1 User

Suggested fields:

- `id`
- `name`
- `email` (unique after normalization)
- `passwordHash`
- `timeZone` (valid IANA time-zone identifier, with a documented default)
- `theme` (such as light, dark, or system)
- `notificationPreferences`
- `xpTotal` and/or level data, if gamification is enabled
- `createdAt`
- `updatedAt`

### 11.2 Task

Suggested fields:

- `id`
- `userId` (owner)
- `title`
- `description`
- `status`
- `taskType` (`one-time` or `daily`)
- `priority`
- `dueAt` (optional timestamp)
- `categoryId` and/or tags
- `estimatedMinutes` (optional)
- `reminderSettings` (optional)
- `currentStreak`
- `bestStreak`
- `lastQualifiedCompletionDay` or equivalent derived/indexed value
- `createdAt`
- `updatedAt`
- `deletedAt` only if soft deletion is selected

Streak counters may be stored for efficient display, but completion history must remain the source of truth or permit reliable reconciliation.

### 11.3 Task Completion / Daily Completion

Suggested fields:

- `id`
- `userId`
- `taskId`
- `completedAt` (server timestamp)
- `completionDay` (the applicable local calendar date, stored unambiguously)
- Optional metadata indicating whether the completion was recovered or protected by a future streak-freeze feature.

A uniqueness constraint or equivalent transactional protection should prevent more than one qualifying completion record for a given task and completion day.

### 11.4 Category

Suggested fields:

- `id`
- `userId`
- `name`
- `color` or icon identifier (optional)
- `createdAt`
- `updatedAt`

### 11.5 Focus Session

Suggested fields:

- `id`
- `userId`
- `taskId` (optional)
- `startedAt`
- `endedAt` (optional while active)
- `durationSeconds`
- `status` (such as active, completed, or cancelled)
- `createdAt`

### 11.6 Achievement / User Achievement

Suggested fields:

- Achievement definition: `id`, `key`, `name`, `description`, `criteria`, and reward metadata.
- User achievement: `id`, `userId`, `achievementId`, `earnedAt`.
- Enforce uniqueness so a one-time achievement is not awarded repeatedly to the same user.

### 11.7 Subtask / Checklist Item

Suggested fields:

- `id`
- `userId`
- `taskId`
- `title`
- `isCompleted`
- `position`
- `createdAt`
- `updatedAt`

## 12. API and Backend Requirements

The backend may use REST or another clearly documented API style. If a REST API is used, it should provide equivalent capabilities to the following endpoint groups.

### 12.1 Authentication and Profile

- `POST /api/auth/register` — create an account.
- `POST /api/auth/login` — authenticate a user.
- `POST /api/auth/logout` — end the session where supported by the chosen authentication strategy.
- `GET /api/users/me` — read the current user's profile.
- `PATCH /api/users/me` — update permitted profile fields.
- `PATCH /api/users/me/password` — change password.
- `DELETE /api/users/me` — delete the current account after confirmation/re-authentication.
- Optional password-recovery endpoints if recovery is implemented.

### 12.2 Tasks

- `POST /api/tasks` — create a task.
- `GET /api/tasks` — list the current user's tasks, with supported filters, sorting, pagination, and search.
- `GET /api/tasks/:taskId` — get one owned task.
- `PATCH /api/tasks/:taskId` — update an owned task.
- `DELETE /api/tasks/:taskId` — delete an owned task.
- `POST /api/tasks/:taskId/complete` — record a completion through a server-validated operation.
- `POST /api/tasks/:taskId/reopen` — reopen a task if supported.

### 12.3 Streaks, Planning, and Insights

- Provide endpoints or service operations for today's plan, task streak details, completion history, focus sessions, achievements, and analytics as needed.
- The server shall calculate or validate streak and XP changes; clients shall not submit trusted final counter values.
- API responses shall use a consistent format for success, validation errors, authentication errors, authorization errors, not-found errors, and unexpected server errors.
- List endpoints should support pagination or sensible limits to avoid returning an unbounded amount of data.

## 13. Security and Privacy Requirements

- **SEC-01:** Enforce authentication on every private API route.
- **SEC-02:** Enforce ownership authorization on every task, category, completion, focus session, subtask, and user-achievement operation.
- **SEC-03:** Never rely solely on a client-provided user ID to determine data ownership.
- **SEC-04:** Hash passwords using a modern password-hashing algorithm with appropriate parameters.
- **SEC-05:** Keep signing keys, database credentials, email credentials, and other secrets in environment variables or a managed secret store.
- **SEC-06:** Validate and normalize incoming input on the server, including IDs, lengths, enums, timestamps, filters, and pagination parameters.
- **SEC-07:** Use safe database queries and prevent injection vulnerabilities.
- **SEC-08:** Configure CORS for approved frontend origins rather than allowing arbitrary origins in production without a deliberate reason.
- **SEC-09:** Use HTTPS in production and secure cookie settings if cookie-based authentication is selected.
- **SEC-10:** Apply rate limiting to sensitive endpoints such as login, registration, and password recovery.
- **SEC-11:** Do not log passwords, authentication tokens, password-reset tokens, or sensitive personal information.
- **SEC-12:** Return only fields the client is authorized to see; never return password hashes in profile responses.
- **SEC-13:** Use safe error messages that do not reveal secrets, internal stack traces, or unnecessary account information.
- **SEC-14:** Account deletion shall include associated user-owned records and any applicable external data, subject to the documented retention policy.

## 14. Non-Functional Requirements

### 14.1 Performance

- **NFR-01:** Common actions such as opening the task list, checking off a task, and viewing today's dashboard should feel responsive under normal operating conditions.
- **NFR-02:** The application shall avoid unnecessary full-page reloads for routine CRUD actions.
- **NFR-03:** Database queries for a user's tasks and completion history shall be appropriately indexed for expected access patterns.
- **NFR-04:** Lists with large numbers of records shall use pagination, limits, or another scalable loading strategy.

### 14.2 Reliability and Data Integrity

- **NFR-05:** Task creation, updates, completion, and deletion shall provide clear success or failure feedback.
- **NFR-06:** Failed requests shall not leave the client displaying an unconfirmed change as if it were saved.
- **NFR-07:** Streak, completion, and XP updates shall be consistent under retry, duplicate, and concurrent requests.
- **NFR-08:** The system shall preserve completion history reliably enough to recalculate streaks and analytics if cached counters become inconsistent.
- **NFR-09:** Production data should be backed up according to the deployment's recovery requirements.

### 14.3 Usability and Accessibility

- **NFR-10:** Core task actions shall require minimal navigation and be usable on a narrow mobile screen.
- **NFR-11:** Forms shall provide understandable validation messages.
- **NFR-12:** Interactive controls shall be keyboard accessible and should use appropriate labels and semantic elements.
- **NFR-13:** The interface shall remain understandable without relying exclusively on color, animation, or icons.

### 14.4 Maintainability

- **NFR-14:** Separate interface, API/controller, business-logic/service, data-model, and validation responsibilities where appropriate.
- **NFR-15:** Keep streak calculations and reward rules in testable backend business logic rather than duplicating them across UI components.
- **NFR-16:** Use consistent naming, formatting, error handling, and API response conventions.
- **NFR-17:** Document environment variables, installation, development commands, database setup, and deployment configuration.
- **NFR-18:** Include automated tests for critical account, task, authorization, and streak behavior.

### 14.5 Compatibility and Configuration

- **NFR-19:** Support current major desktop and mobile browsers.
- **NFR-20:** Keep environment-specific configuration outside source code.
- **NFR-21:** Dates must be stored and processed consistently (normally UTC timestamps plus the user's IANA time zone and the qualifying local completion date).

## 15. Validation and Error-Handling Requirements

- Reject missing or whitespace-only task titles.
- Reject invalid task status, task type, priority, time zone, and malformed identifiers.
- Reject invalid due dates or reminder values according to documented rules.
- Return `401 Unauthorized` or the equivalent when authentication is absent or invalid.
- Return `403 Forbidden` or a privacy-preserving `404 Not Found` when a user attempts to access another user's record.
- Return `404 Not Found` when a requested record does not exist or is unavailable to the user.
- Return a clear client error for invalid request data without exposing internal implementation details.
- Handle network failure, expired sessions, server failure, and database failure gracefully.
- Prevent multiple clicks or request retries from producing duplicate completions, XP, achievements, or focus-session records.

## 16. Acceptance Criteria

The initial release is acceptable when the following scenarios pass:

### 16.1 Account and Privacy

- A new user can register with valid information and cannot register a duplicate normalized email.
- A user can log in and log out successfully.
- An unauthenticated visitor cannot access protected user data.
- Two separate accounts see separate profiles, tasks, histories, and statistics.
- A user cannot read, edit, complete, or delete another user's task by substituting its ID in a request.
- A user can edit their profile and delete their account through the documented flow.

### 16.2 Task CRUD

- A user can create a task, view it, edit it, mark it complete, and delete it.
- Invalid task data is rejected with useful feedback.
- Search, sorting, filters, and task views return only the user's tasks.
- A completed one-time task appears in the completed view and no longer appears as an outstanding task by default.

### 16.3 Streak Behavior

- Creating a daily task starts its streak at `0`.
- Completing it for the first time on a given local day establishes a streak of `1`.
- Completing it on the next consecutive local day increases the streak to `2`.
- Completing it multiple times on the same local day counts as one day only.
- Missing a required day resets the current streak according to Section 7, while preserving the best streak.
- A completion at or after local midnight is credited to the new day, not the previous day.
- Streak calculations remain correct when the user time zone differs from UTC.
- A one-time task does not accidentally receive a daily streak.

### 16.4 Stand-Out Features

- The Today view brings due, overdue, and uncompleted daily tasks together and provides explainable task-order suggestions.
- A focus session can be started, paused/resumed, stopped, and included in focus-time summaries when the focus feature is enabled.
- XP and achievements are awarded according to defined rules and are not duplicated by repeated requests.
- Weekly insights are calculated from the signed-in user's records and show their reporting period.
- Checklist items can be managed and their progress is visible on their parent task when subtasks are enabled.

### 16.5 Quality

- The application works on desktop and mobile layouts.
- Loading, empty, success, validation, and error states are present for core flows.
- Critical backend logic has automated tests, especially authorization and streak boundaries.
- Setup instructions allow another developer to configure and run the project from a clean checkout.

## 17. Testing Requirements

### 17.1 Unit Tests

Test isolated business logic for:

- Streak initialization, increment, reset, and best-streak preservation.
- Local-day calculation and midnight boundary handling.
- Duplicate daily completion prevention.
- Task validation and status transitions.
- XP and achievement eligibility rules.
- Completion-rate and weekly-insight calculations.

### 17.2 API / Integration Tests

Test:

- Registration, duplicate-email handling, login, and protected routes.
- Each task CRUD operation.
- Ownership checks across two different users.
- Completing a daily task more than once on the same day.
- Completing a daily task on consecutive days and after a missed day.
- Profile update and account deletion behavior.
- Focus-session recording and reward idempotency if those features are enabled.

### 17.3 UI / End-to-End Tests

Test the main user journey:

1. Register and log in.
2. Create a one-time task and a daily task.
3. Edit a task and use search/filter controls.
4. Complete a one-time task.
5. Complete a daily task and confirm the displayed streak.
6. View dashboard and progress summaries.
7. Log out and confirm protected screens are no longer accessible.

## 18. Recommended Implementation Priorities

### Phase 1 — Core MVP

- Registration, login, logout, and profile management.
- User-private task CRUD.
- Task status, priority, due date, search, filters, and sorting.
- Daily task type and reliable streak history/calculation.
- Responsive dashboard and Today / All Tasks / Completed views.
- Input validation, authorization, error states, and tests for security and streak rules.

### Phase 2 — Differentiating Productivity Features

- Smart Daily Plan and top-priority tasks.
- Focus timer and focus-session history.
- XP, levels, and achievements.
- Weekly insights and progress analytics.
- Checklists and subtasks.

### Phase 3 — Optional Enhancements

- Reminders and external notifications.
- Streak Freeze or recovery mechanics.
- Additional recurrence patterns (weekly or custom days), calendar integrations, data export, and mobile applications.

Features in later phases should not delay a secure, reliable core task and streak experience.

## 19. Open Decisions to Record Before Implementation

The following choices should be documented in the project README or technical design before the relevant feature is built:

- The chosen frontend, backend, database, and authentication technologies.
- Whether authentication uses secure cookies/sessions or bearer tokens, and the associated security configuration.
- The default time zone for new accounts and whether users may change it after creating completion history.
- Whether task deletion is permanent or uses soft deletion and how long historical records are retained.
- Whether reopening a completed task is supported and how it affects completion history and XP.
- The exact XP formula, level thresholds, and achievement criteria.
- Which optional features are part of the first release, especially reminders, Streak Freeze, and password recovery.
- Whether future recurring patterns beyond daily tasks will be supported and how missed days are defined for those patterns.

---

**End of document.**
