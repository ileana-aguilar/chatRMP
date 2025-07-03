import { render, screen, fireEvent } from "@testing-library/react";
import Chatbot from "./Chatbot";

describe("Chatbot component", () => {
  test("renders input and send button", () => {
    render(<Chatbot />);
    expect(screen.getByPlaceholderText(/Ask about professors.../i)).toBeInTheDocument();
    expect(screen.getByText(/Send/i)).toBeInTheDocument();
  });

  test("can type and send a message", () => {
    render(<Chatbot />);
    const input = screen.getByPlaceholderText(/Ask about professors.../i);
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(screen.getByText(/Send/i));
    expect(input.value).toBe("");
  });
});
