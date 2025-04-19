import mongoose from "mongoose";
import { DB_NAME } from "../constants.js";
const connectDB = async () => {
  try {
    const connectioninstance = await mongoose.connect(
      `${process.env.MONGODB_URI}`
    );
    console.log(
      `\n MOngoDb connected ! DB host:${connectioninstance.connection.host}`
    );
  } catch (error) {
    console.log("MongoDb connection error", error);
    process.exit(1);
  }
};
export default connectDB;
