import dotenv from "dotenv";
dotenv.config({
  //to configure the the env file
  path: ".env",
});
import schedule from "node-schedule";
import Reminder from "../models/Reminder.js";
import nodemailer from "nodemailer";
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});


console.log("EMAIL_USER:", process.env.EMAIL_USER);
console.log("EMAIL_PASS:", process.env.EMAIL_PASS);

function isDueTomorrow(dateStr) {
  const vaccineDate = new Date(dateStr);
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  return (
    vaccineDate.getFullYear() === tomorrow.getFullYear() &&
    vaccineDate.getMonth() === tomorrow.getMonth() &&
    vaccineDate.getDate() === tomorrow.getDate()
  );
}

// ✅ Exportable function to send immediate email if due tomorrow
const sendImmediateReminderIfDueTomorrow = async (reminder) => {
  if (isDueTomorrow(reminder.vaccineDate)) {
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: reminder.ownerEmail,
      subject: `Reminder: ${reminder.petName}'s ${reminder.vaccineName} is due tomorrow!`,
      text: `Hi petbuddy 🐾! Just a quick reminder that ${
        reminder.petName
      } has a ${
        reminder.vaccineName
      } vaccine scheduled for tomorrow (${new Date(
        reminder.vaccineDate
      ).toDateString()}). `,
    };

    try {
      await transporter.sendMail(mailOptions);
      console.log("✅ Immediate reminder email sent.");
    } catch (err) {
      console.error("❌ Error sending email:", err);
    }
  }
};

// ✅ Scheduled job: sends reminder 3 days before
const scheduleReminders = () => {
  schedule.scheduleJob("0 9 * * *", async function () {
    const today = new Date();
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + 3);

    const reminders = await Reminder.find({
      vaccineDate: {
        $gte: today,
        $lte: targetDate,
      },
    });

    reminders.forEach((reminder) => {
      const mailOptions = {
        from: process.env.EMAIL_USER,
        to: reminder.ownerEmail,
        subject: `Reminder: ${reminder.petName}'s ${reminder.vaccineName}`,
        text: `Hi! ${reminder.petName} has a ${
          reminder.vaccineName
        } vaccine due on ${new Date(reminder.vaccineDate).toDateString()}.`,
      };

      transporter.sendMail(mailOptions);
    });
  });
};
export { sendImmediateReminderIfDueTomorrow, scheduleReminders };
