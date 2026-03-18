import React, { useState, useRef } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Stack,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

const Chatbot = () => {
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const chatBoxRef = useRef(null);

  const handleKeyPress = (event) => {
    if (event.key === "Enter") sendMessage();
  };

  const sendMessage = () => {
    const trimmedInput = userInput.trim();
    if (!trimmedInput) return;

    const time = new Date().toLocaleTimeString();

    const userMsg = {
      type: "user",
      content: trimmedInput,
      time: time,
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setUserInput("");

    fetch("http://localhost:5000/get", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ msg: trimmedInput }),
    })
      .then((response) => response.text())
      .then((data) => {
        const botMsg = {
          type: "bot",
          content: data,
          time: new Date().toLocaleTimeString(),
        };
        setChatMessages((prev) => [...prev, botMsg]);

        setTimeout(() => {
          chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
        }, 100);
      })
      .catch((error) => console.error("Error:", error));
  };

  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        bgcolor: "#0f3460",
        p: 2,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          width: "100%",
          maxWidth: "900px",
          height: "90vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Box
          display="flex"
          alignItems="center"
          p={2}
          bgcolor="#16213e"
          color="white"
        >
          <Avatar src="/static/Avatar.png" />
          <Box ml={2}>
            <Typography variant="h6">Medical Chatbot</Typography>
            <Typography variant="body2">Ask me anything!</Typography>
          </Box>
        </Box>

        <Box
          ref={chatBoxRef}
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 2,
            bgcolor: "#1a1a2e",
          }}
        >
          {chatMessages.map((msg, index) => (
            <Stack
              key={index}
              direction={msg.type === "user" ? "row-reverse" : "row"}
              spacing={2}
              mb={2}
              alignItems="flex-start"
            >
              <Avatar
                src={
                  msg.type === "user"
                    ? "/static/user.png"
                    : "/static/Avatar.png"
                }
              />

              <Box>
                <Paper
                  elevation={2}
                  sx={{
                    p: 1.5,
                    maxWidth: "75%",
                    bgcolor: msg.type === "user" ? "#00a884" : "#3b82f6",
                    color: "white",
                  }}
                >
                  <Typography variant="body1">{msg.content}</Typography>
                </Paper>
                <Typography variant="caption" color="#ccc">
                  {msg.time}
                </Typography>
              </Box>
            </Stack>
          ))}
        </Box>

        <Box display="flex" alignItems="center" p={2} bgcolor="#16213e">
          <TextField
            fullWidth
            variant="filled"
            placeholder="Type a message..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              backgroundColor: "#1a1a2e",
              borderRadius: "25px",
              input: { color: "white" },
              "& .MuiFilledInput-root": { backgroundColor: "#1a1a2e" },
            }}
          />
          <IconButton
            color="primary"
            onClick={sendMessage}
            sx={{
              ml: 1,
              bgcolor: "#00a884",
              "&:hover": { bgcolor: "#00826e" },
            }}
          >
            <SendIcon sx={{ color: "white" }} />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default Chatbot;
