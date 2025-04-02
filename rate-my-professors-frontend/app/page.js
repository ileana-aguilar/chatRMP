import Navbar from "./components/Navbar";
import Chatbot from "./components/Chatbot";

export default function Home() {
  return (
    <div className="bg-gray-100 min-h-screen pt-16"> 
      <Navbar />
      <div className="flex items-center justify-center">
        <Chatbot />
      </div>
    </div>
  );
}
