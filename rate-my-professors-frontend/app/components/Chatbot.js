"use client";
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import styles from "./Chatbot.module.css";

const backendURL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [loadingDots, setLoadingDots] = useState("");
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesContainerRef = useRef(null);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

    if (loading) {
      const interval = setInterval(() => {
        setLoadingDots((prev) => (prev.length < 3 ? prev + "." : ""));
      }, 500);
      return () => clearInterval(interval);
    }
  }, [messages, loading]);

  

  useEffect(() => {
    const scrollContainer = document.querySelector("body");
  
    const handleScroll = () => {
      if (!scrollContainer) return;
  
      const isAtBottom =
        scrollContainer.scrollHeight - scrollContainer.scrollTop <= scrollContainer.clientHeight + 10;
  
      setShowScrollButton(!isAtBottom);
      
    };
  
    scrollContainer.addEventListener("scroll", handleScroll);
    handleScroll(); 
  
    return () => {
      scrollContainer.removeEventListener("scroll", handleScroll);
    };
  }, []);
  
  
  
  
  

  const handleSendMessage = async (customQuery = null) => {
    const input = customQuery ?? query;
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setQuery("");
    setLoading(true);

    const greetingPatterns = ["hi", "hello", "hey", "good morning", "good evening"];
    const generalPatterns = ["how are you", "what can you do", "help"];

    if (greetingPatterns.includes(input.toLowerCase())) {
      setLoading(false);
      animateBotMessage("Hi! What can I help you with today?");
      return;
    }

    if (generalPatterns.some((pattern) => input.toLowerCase().includes(pattern))) {
      setLoading(false);
      animateBotMessage(
        "I can help you find the best professors! Just ask me about a professor or department."
      );
      return;
    }

    try {
      const response = await axios.post(`${backendURL}/search_professors`, {
        query: input.trim(),
        department: null,
      });

      setLoading(false);
      if (Array.isArray(response.data.response)) {
        for (const professor of response.data.response) {
          const message = `${professor.name} (${professor.department}) - Rating: ${professor.rating}.\n${professor.reasoning}`;
          animateBotMessage(message);
        }
      } else {
        animateBotMessage(response.data.response);
      }
    } catch (error) {
      setLoading(false);
      console.error("Error fetching response:", error);
      animateBotMessage("Something went wrong. Please try again.");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const animateBotMessage = (fullText) => {
    let words = fullText.split(" ");
    let currentText = "";
    let index = 0;

    const interval = setInterval(() => {
      if (index < words.length) {
        currentText += words[index] + " ";
        setMessages((prevMessages) => [
          ...prevMessages.slice(0, -1),
          { text: currentText, sender: "bot" },
        ]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 50);

    setMessages((prevMessages) => [...prevMessages, { text: "", sender: "bot" }]);
  };

  const getMatchingSuggestions = () => {
    const baseSuggestions = [
      "Who is the best professor in",
      "Who is the worst professor in",
      "List professors in the",
      "Tell me about Professor"
    ];

    const departments = ["Math", "Computer Science", "English", "Biology", "Physics"];
    const professors = ["Erica Doran", "John Nici", "Mary Greiner", "Nourit Zimerman"];
    const userInput = query.trim().toLowerCase();

    if (!userInput) return [];

    const normalizedInput = userInput.toLowerCase().trim();

    const matchedBase = baseSuggestions.find(base =>
      normalizedInput.startsWith(base.toLowerCase().trim()) ||
      base.toLowerCase().trim().startsWith(normalizedInput)
    );

    if (!matchedBase) return [];

    const source = matchedBase.includes("Tell me about Professor") ? professors : departments;

    return source.map(name => {
      const suggestionText = matchedBase.includes("Tell me about Professor")
        ? `${matchedBase} ${name}?`
        : `${matchedBase} ${name} department?`;

      const regex = new RegExp(`(${userInput})`, "i");
      const parts = suggestionText.split(regex);

      const highlighted = parts.map((part, i) =>
        regex.test(part) ? <strong key={i}>{part}</strong> : <span key={i}>{part}</span>
      );

      return { text: suggestionText, highlighted };
    });
  };

  return (
    <>
    {showScrollButton && (
      <button
        className={styles.scrollToBottomButton}
        onClick={() => {
          const scrollContainer = document.querySelector("body");
          scrollContainer?.scrollTo({ top: scrollContainer.scrollHeight, behavior: "smooth" });
        }}
        
      >
        ⬇️
      </button>
   )}
    <div
      className={`${styles.chatContainer} ${
        messages.length === 0 && !loading ? styles.centeredContainer : ""
      }`}
    >
      
      <div className={styles.messages} ref={messagesContainerRef}>
        {messages.length === 0 && !loading && (
          <div className={`${styles.emptyState} ${styles.itemsEnd}`}>
            <h2 className={`${styles.title} ${styles.justifyCenter}`}>
              What can I help with?
            </h2>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`${styles.messageWrapper} ${
              msg.sender === "user" ? styles.alignRight : styles.alignLeft
            }`}
          >
            <div
              className={`${styles.message} ${
                msg.sender === "user" ? styles.userMessage : styles.botMessage
              }`}
            >
              {msg.text.split("\n").map((line, idx) => (
                <React.Fragment key={idx}>
                  {line}
                  <br />
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}

        {loading && (
          <div className={styles.typingIndicator}>
            Chatbot is typing{loadingDots}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 0 &&
        getMatchingSuggestions().length > 0 &&
        query.trim().length > 0 && (
          <div className={styles.suggestionBox}>
            {getMatchingSuggestions().map((item, index) => (
              <div
                key={index}
                className={styles.suggestionItem}
                onClick={() => {
                  setQuery(item.text);
                  handleSendMessage(item.text);
                }}
              >
                {item.highlighted}
              </div>
            ))}
          </div>
        )}

      <div
        className={`${styles.chatInputContainer} ${
          messages.length > 0 ? styles.chatInputFixed : ""
        }`}
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask about professors..."
          className={styles.chatInput}
        />
        <button onClick={handleSendMessage} className={styles.sendButton}>
          Send
        </button>
      </div>

      {messages.length === 0 && (
        <div className={`${styles.promptButtons} ${styles.justifyCenter}`}>
          <button
            onClick={() => {
              const text = "Who is the best professor in";
              if (query === text) return;
              setQuery(text);
            }}
          >
            👩‍🏫 Best Professor
          </button>
          <button
            onClick={() => {
              const text = "Who is the worst professor in";
              if (query === text) return;
              setQuery(text);
            }}
          >
            🙅‍♀️ Worst Professor
          </button>
          <button
            onClick={() => {
              const text = "List professors in the";
              if (query === text) return;
              setQuery(text);
            }}
          >
            📋 List Professors
          </button>
          <button
            onClick={() => {
              const text = "Tell me about Professor";
              if (query === text) return;
              setQuery(text);
            }}
          >
            🔮 Tell me about
          </button>
        </div>
      )}
    </div>
    </>
  );
  
};

export default Chatbot;
