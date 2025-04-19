import dotenv from "dotenv";
dotenv.config({
  //to configure the the env file
  path: ".env",
});
import express from "express";
import connectDB from "./config/db.js";
import reminderRoutes from "./routes/reminderRoutes.js";
import { scheduleReminders } from "./utils/sendReminderEmails.js";
import cors from "cors";


const app = express();
app.use(express.json());
app.use(cors());
connectDB();
scheduleReminders();

app.use("/", reminderRoutes);

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
