
import express from "express";
import { Router } from "express";
import Reminder from "../models/Reminder.js";
import { sendImmediateReminderIfDueTomorrow } from "../utils/sendReminderEmails.js";

const router = Router();
router.post("/add-reminder", async (req, res) => {
  const { petName, ownerEmail, vaccineName, vaccineDate } = req.body;
  if (!petName || !ownerEmail || !vaccineName || !vaccineDate) {
    return res.status(400).json({ error: "Missing fields" });
  }
  try {
    const reminder = new Reminder({
      petName,
      ownerEmail,
      vaccineName,
      vaccineDate,
    });
    await reminder.save();
    await sendImmediateReminderIfDueTomorrow(reminder); // ✅ Trigger mail if needed
    res.status(201).json({ message: "Reminder set successfully!" });
  } catch (err) {
    console.error("Error saving reminder:", err);
    res.status(500).json({ error: "Something went wrong on the server." });
  }
});

router.get("/reminders", async (req, res) => {
  const reminders = await Reminder.find();
  res.json(reminders);
});

export default router;
