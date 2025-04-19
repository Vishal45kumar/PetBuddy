
import mongoose from "mongoose"
const reminderSchema = new mongoose.Schema({
  petName: String,
  ownerEmail: String,
  vaccineName: String,
  vaccineDate: Date,
});

const Reminder= mongoose.model("Reminder", reminderSchema);
export default Reminder
