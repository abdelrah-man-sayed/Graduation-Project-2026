# Data Flow Diagram (DFD) Documentation

## Document Purpose

This document provides a professional and detailed explanation of the backend Data Flow Diagram (DFD) for the soccer field booking platform.
It is intended for project documentation, technical review, and handoff to academic or development stakeholders.

## System Context

The backend is a Django REST API that serves a mobile booking application.
The current implementation supports the following primary actors:

- `Player App`: a customer-facing mobile client for browsing courts, placing bookings, submitting reviews, and managing profile data.
- `Owner App`: a court owner mobile client for managing court listings, responding to booking requests, viewing analytics, and controlling court availability.
- `Admin UI`: the Django admin interface used for server-side data inspection and management.

## DFD Description

The system is represented by the following logical components and their data relationships:

- **Player Mobile App** interacts with the backend to browse active courts, submit booking requests, post reviews, request password reset OTP codes, and update profile data.
- **Owner Mobile App** interacts with the backend to create and edit courts, toggle court availability, manage booking approvals, view analytics, and update profile data.
- **Admin Django Site** provides administrative access to backend data and uses the same authentication service as the mobile apps.

The backend is split into the following process domains:

- **Auth Service**: handles signup, login, and token refresh.
- **User Profile Service**: retrieves and updates personal user data, and supports account deletion.
- **Field Service**: manages field/court creation, updates, image upload, and status toggling.
- **Booking Service**: processes booking requests, validates availability, and updates booking state.
- **Review Service**: accepts rating submissions and exposes written reviews.
- **Owner Dashboard Service**: aggregates metrics from court and booking data for owner analytics.
- **Password Reset Service**: stores OTP codes and handles email-based OTP reset flows.

The following external services and storage components are involved:

- **Cloudinary Media Storage**: stores uploaded court images.
- **SMTP Email Service**: sends OTP codes for password reset.
- **Database**: stores users, courts, images, bookings, reviews, and OTP records.

The overall data flow is:

1. External apps authenticate through the Auth Service and receive JWT tokens.
2. Authenticated requests route to the appropriate service domain.
3. Field operations update `Fields` and `FieldImages` storage and may use Cloudinary for media upload.
4. Booking operations validate availability against `Fields` and `Bookings` storage, then persist reservation data.
5. Review operations validate booking history and persist ratings/comments to `Review` storage.
6. Owner dashboard operations aggregate metrics from `Fields` and `Bookings` storage.
7. Password reset operations use `PasswordResetOTP` storage and SMTP email delivery.

## Implemented Data Flows

BookingAPI -->|Validate availability| Database

ReviewAPI -->|Read/write review data| Database
ReviewAPI -->|Read review summary| Database

DashboardAPI -->|Aggregate metrics| Database
ProfileAPI -->|Read/update user data| Database
OTPAPI -->|Store OTP record| Database
OTPAPI -->|Send OTP email| EmailService
AuthAPI -->|Read/write users| Database
AdminUI -->|Manage all tables| Database

```

## DFD Structure and Components

### External Entities

- **Player App**: initiates user-facing actions, including search, booking, review submission, and password reset.
- **Owner App**: manages court listings and booking responses, and consumes dashboard analytics.
- **Admin UI**: used by administrators for backend data access through Django admin.

### Process Blocks

Each process block in this DFD represents a backend service or API responsibility.

- **Auth Service**: handles login, signup, and token refresh.
- **User Profile Service**: retrieves and updates personal user data, and supports account deletion.
- **Field Service**: manages field/court creation, updates, status toggling, and image uploads.
- **Booking Service**: processes booking requests, validates availability, and updates booking state.
- **Review Service**: accepts rating submissions and exposes written reviews.
- **Owner Dashboard Service**: aggregates booking and revenue metrics for court owners.
- **Password Reset Service**: issues OTP codes and handles password reset transactions.

### Data Stores

The system uses a central relational database intended to store all core domain data.

- **Users**: stores user accounts, profile information, social links, and role type.
- **Fields**: stores court listings, pricing, amenities, geographic data, and active status.
- **FieldImages**: stores metadata related to court images and their association with fields.
- **Bookings**: stores reservation details, status, and total pricing.
- **Review**: stores user ratings and comments for each field.
- **PasswordResetOTP**: stores one-time OTP tokens for resetting user passwords.

### External Services

- **Cloudinary**: stores uploaded court images and returns URLs for field galleries.
- **SMTP Email Service**: sends password reset OTP codes to users by email.

## Detailed Flow Descriptions

### 1. Authentication and User Management

This flow secures the platform and enables identity management.

- Input: email and password.
- Process:
  1. The app sends signup or login credentials to `/api/v1/auth/signup/` or `/api/v1/auth/login/`.
  2. The Auth Service verifies credentials and issues JWT access and refresh tokens.
  3. The client stores the JWT token for future authenticated requests.
- Output: authenticated token pair and user profile data.

### 2. User Profile and Account Management

Users can manage personal data and terminate their account.

- Input: authenticated request with updated profile fields or account deletion confirmation.
- Process:
  1. User sends a request to `/api/v1/users/me/`.
  2. The Profile Service validates user identity and applies updates.
  3. The database stores changes in the `Users` table.
- Output: updated profile data or account deletion confirmation.

### 3. Field/Court Management

Court owners manage the marketplace inventory.

- Input: field metadata, uploaded images, or status change request.
- Process:
  1. Owner sends court data to `/api/v1/fields/` or `/api/v1/fields/{id}/`.
  2. The Field Service stores field metadata in `Fields`.
  3. Uploaded images are forwarded to Cloudinary.
  4. Image metadata is saved to `FieldImages`.
  5. Courts are visible to players only when `is_active=True`.
- Output: active court listings available to the Player App.

### 4. Booking Management

This flow enforces reservation rules and availability.

- Input: booking request containing court, date, and time range.
- Process:
  1. Player sends a request to `/api/v1/bookings/`.
  2. The Booking Service checks existing booking entries for conflicts.
  3. If valid, it computes total price and stores the booking as `pending`.
  4. Owners update the booking status via `/accept/` or `/decline/`.
- Output: booking acceptance or rejection state.

### 5. Review and Rating Management

Players may rate and review courts after confirmed bookings.

- Input: review payload and authenticated user identity.
- Process:
  1. The Review Service enforces that the user has a confirmed booking.
  2. It stores rating and comment data in `Review`.
  3. Field listings surface average rating and review count.
- Output: published review and updated field rating summary.

### 6. Owner Dashboard Analytics

Court owners consume operational and financial metrics.

- Input: dashboard request from an authenticated owner.
- Process:
  1. The Dashboard Service aggregates records from `Fields` and `Bookings`.
  2. It computes totals for active courts, pending requests, today’s bookings, and weekly revenue.
  3. It returns chart-ready revenue data.
- Output: dashboard summary for owners.

### 7. Password Reset with OTP

This flow handles secure password recovery.

- Input: email address and OTP, followed by a new password.
- Process:
  1. The user requests an OTP through `/api/v1/auth/request-otp/`.
  2. The OTP Service stores the generated code in `PasswordResetOTP`.
  3. The code is delivered via SMTP email.
  4. The user submits the OTP and new password to `/api/v1/auth/reset-password-otp/`.
  5. The backend validates the OTP and updates the password.
- Output: password reset confirmation.

## Assumptions and Scope

- The DFD reflects only the currently implemented backend processes.
- Unexposed models such as `Payments`, `Notifications`, and `Messages` are excluded from the active DFD.
- The diagram assumes that all authenticated requests are protected by JWT-based authorization.

## Summary of Current System Coverage

The diagram and documentation cover the following active backend responsibilities:

- user onboarding and authentication
- profile management
- court listing lifecycle
- booking lifecycle and approval
- review submission and validation
- owner analytics reporting
- OTP-based password recovery
- image storage and email delivery integration

## How to Use This Documentation

This document is suitable for:

- technical handoff to reviewers and academic evaluators
- supporting the diagram in a formal documentation folder
- aligning frontend development with backend responsibilities

Use the diagram in conjunction with the endpoint list and flow descriptions to verify the implementation against the system design.
```
