# Beauty Booking Bot

An automated appointment booking system for beauty professionals. Clients book appointments via Instagram DMs and WhatsApp, and appointments automatically sync to Google Calendar with automated reminders.

## Features

- **Multi-platform**: Instagram DMs and WhatsApp messaging
- **Automatic Calendar Sync**: Appointments instantly appear in Google Calendar
- **Client Management**: Store client names, phone numbers, and booking history
- **Rescheduling & Cancellation**: Clients can reschedule or cancel via DM
- **Automated Reminders**: Send reminders 1 day before and 1 hour before appointments
- **Turkish Language**: Fully localized for Turkish-speaking clients
- **Easy Configuration**: Simple JSON config file for business setup

## Architecture

```
Instagram DMs / WhatsApp → Node.js Backend → PostgreSQL Database
                                    ↓
                          Google Calendar API
                                    ↓
                          Automated Reminders
```

## Tech Stack

- **Backend**: Node.js + Express
- **Database**: PostgreSQL
- **Messaging APIs**: Meta Graph API (Instagram), Twilio (WhatsApp)
- **Calendar**: Google Calendar API
- **Deployment**: Railway or Render
- **Scheduling**: node-cron

## Project Structure

```
beauty-booking-bot/
├── README.md
├── DEPLOYMENT.md
├── config.json (Client configuration)
├── .env.example
├── package.json
├── src/
│   ├── index.js (Main server)
│   ├── meta-handler.js (Instagram DMs)
│   ├── twilio-handler.js (WhatsApp)
│   ├── calendar-handler.js (Google Calendar integration)
│   ├── database.js (PostgreSQL operations)
│   ├── reminder-scheduler.js (Automated reminders)
│   └── utils/
│       ├── messages.js (Turkish templates)
│       ├── validators.js (Business logic)
│       └── helpers.js (Utility functions)
├── migrations/
│   └── init.sql (Database schema)
└── .gitignore
```

## Database Schema

### clients table
```sql
CREATE TABLE clients (
  id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(50) UNIQUE NOT NULL,
  business_name VARCHAR(255),
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### bookings table
```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(50) REFERENCES clients(tenant_id),
  customer_name VARCHAR(255),
  customer_phone VARCHAR(20),
  service_id VARCHAR(50),
  booking_date TIMESTAMP,
  google_event_id VARCHAR(255),
  reminder_24h_sent BOOLEAN DEFAULT FALSE,
  reminder_1h_sent BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) DEFAULT 'confirmed',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Configuration

Edit `config.json` to customize for each client:

```json
{
  "business_name": "Ayşe's Eyebrow Studio",
  "phone": "+905551234567",
  "services": [
    {
      "name": "Kaş Alma",
      "duration_minutes": 30,
      "price": 50,
      "id": "eyebrow_shaping"
    }
  ],
  "business_hours": {
    "monday": { "open": "10:00", "close": "18:00" },
    "tuesday": { "open": "10:00", "close": "18:00" },
    "wednesday": null,
    "thursday": { "open": "10:00", "close": "18:00" },
    "friday": { "open": "10:00", "close": "20:00" },
    "saturday": { "open": "10:00", "close": "16:00" },
    "sunday": null
  },
  "booking_rules": {
    "min_advance_hours": 24,
    "allow_same_day": false,
    "timezone": "Europe/Istanbul"
  },
  "reminders": {
    "enabled": true,
    "send_1_day_before": true,
    "send_1_hour_before": true
  }
}
```

## Environment Variables

Create a `.env` file (see `.env.example`):

```
# Meta (Instagram)
META_PAGE_ACCESS_TOKEN=your_token
META_VERIFY_TOKEN=your_verify_token

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Google Calendar
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Database
DATABASE_URL=postgresql://user:pass@host:port/database

# App
TENANT_ID=unique_client_id
NODE_ENV=production
PORT=3000
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/beauty-booking-bot.git
   cd beauty-booking-bot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set up database**
   ```bash
   npm run migrate
   ```

5. **Start the server**
   ```bash
   npm start
   ```

## Booking Flow

### Instagram/WhatsApp Conversation

```
Client: "Merhaba"
Bot: "Hoşgeldiniz! 👋 Hangi hizmeti almak istiyorsunuz?"
     [Kaş Alma - 30 dk]
     [Kaş Tasarımı - 45 dk]

Client: "Kaş Alma"
Bot: "Hangi tarihte randevu istiyorsunuz? (YYYY-MM-DD)"

Client: "2025-10-20"
Bot: "Hangi saatte randevu istiyorsunuz?"
     [10:00, 11:00, 14:00, 15:00]

Client: "14:00"
Bot: "Adınız?"

Client: "Fatma"
Bot: "Telefon numaranız?"

Client: "+905559876543"
Bot: "✅ Randevu onaylandı!"
     "Tarih: 20 Ekim 2025"
     "Saat: 14:00"
     "Hizmet: Kaş Alma (30 dk)"
```

### Rescheduling

```
Client: "Randevuyu değiştirmek istiyorum"
Bot: "Mevcut randevularınız:"
     [20 Ekim 14:00 - Kaş Alma]

Client: "20 Ekim 14:00"
Bot: [Proceeds with new date/time selection]
```

### Cancellation

```
Client: "Randevuyu iptal etmek istiyorum"
Bot: "Mevcut randevularınız:"
     [20 Ekim 14:00 - Kaş Alma]

Client: "20 Ekim 14:00"
Bot: "✅ Randevu iptal edildi."
```

## Deployment

For detailed deployment instructions on Railway or Render, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Start

1. Create Railway/Render account
2. Connect your GitHub repository
3. Set environment variables in the dashboard
4. Deploy

The server will start automatically and begin accepting bookings.

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/webhook/instagram` | Instagram DM webhook |
| POST | `/webhook/whatsapp` | WhatsApp webhook |
| GET | `/health` | Health check |

## Reminders

Automated reminders are sent via WhatsApp/Instagram:
- **24 hours before**: "Yarın saat 14:00'de randevu hatırlatıcısı..."
- **1 hour before**: "1 saat içinde randevu..."

Reminders are only sent once per appointment.

## Notes for Deployment Team

- Each client gets a separate deployment with their own database and credentials
- The business specialist sees all bookings in their Google Calendar
- Payment tracking is handled separately by the specialist
- Config.json can be edited and redeployed as needed
- Timezone is set to Europe/Istanbul by default (can be changed in config)

## Future Enhancements

- Multiple staff members support
- Payment integration
- Client review system
- Advanced analytics dashboard
- Mobile app

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.# beauty-booking-bot
