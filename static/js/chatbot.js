// ── LIBRARY CHATBOT ────────────────────────────────────────────────────────

const BOT_RESPONSES = [
  {
    patterns: ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste'],
    replies: [
      "Hey! 👋 I'm Lib, your library assistant. How can I help you today?",
      "Hello there! Ask me anything about the library system.",
      "Hi! I'm here to help with books, members, fines, and more. What do you need?"
    ]
  },
  {
    patterns: ['how to add book', 'add a book', 'new book', 'enter book'],
    replies: [
      "To add a book:\n1. Go to <b>Books</b> in the sidebar\n2. Click <b>+ Add Book</b>\n3. Fill in title, author, ISBN, category & copies\n4. Hit Save!\n\nTip: ISBN must be unique for each book."
    ]
  },
  {
    patterns: ['issue book', 'borrow book', 'how to issue', 'give book'],
    replies: [
      "To issue a book:\n1. Click <b>Issue Book</b> in the sidebar\n2. Select the book (only available ones show up)\n3. Select the member\n4. Choose loan duration (7/14/21/30 days)\n5. Submit!\n\nFine rate: ₹5/day if returned late."
    ]
  },
  {
    patterns: ['return book', 'how to return', 'book return'],
    replies: [
      "To return a book:\n1. Go to <b>Transactions</b>\n2. Find the transaction (Issued/Overdue)\n3. Click the <b>Return</b> button\n\nIf overdue, fine is auto-calculated at ₹5/day."
    ]
  },
  {
    patterns: ['fine', 'penalty', 'overdue', 'late fee', 'how much fine'],
    replies: [
      "Fine policy:\n• Rate: <b>₹5 per day</b> after due date\n• Fines are auto-calculated on return\n• Go to Transactions → click <b>Pay Fine</b> to mark as paid\n\nExample: 5 days late = ₹25 fine."
    ]
  },
  {
    patterns: ['add member', 'new member', 'register member', 'member registration'],
    replies: [
      "To add a member:\n1. Go to <b>Members</b> in the sidebar\n2. Click <b>+ Add Member</b>\n3. Enter name, email, phone\n4. Choose membership type (Standard/Premium/Student)\n5. Set expiry date & save!"
    ]
  },
  {
    patterns: ['membership', 'types', 'premium', 'standard', 'student'],
    replies: [
      "We have 3 membership types:\n• <b>Standard</b> — Basic borrowing rights\n• <b>Premium</b> — Priority reservations, longer loans\n• <b>Student</b> — Discounted, linked to institution\n\nSet/change type in the Edit Member form."
    ]
  },
  {
    patterns: ['category', 'categories', 'genre', 'book type'],
    replies: [
      "To manage categories:\n1. Go to <b>Categories</b> in the sidebar\n2. Type a new category name and click Add\n3. Assign categories when adding/editing books\n\nDefault categories: Fiction, Science, Technology, History, Biography."
    ]
  },
  {
    patterns: ['report', 'analytics', 'statistics', 'stats', 'data', 'dashboard'],
    replies: [
      "The <b>Reports</b> page shows:\n• Total books, members, issued & overdue counts\n• Fine collected vs pending\n• Most borrowed books (bar chart)\n• Most active members\n• Circulation & overdue rates\n\nCheck it in the sidebar under Analytics."
    ]
  },
  {
    patterns: ['search', 'find book', 'look up', 'search book'],
    replies: [
      "You can search books by:\n• Title\n• Author name\n• ISBN number\n\nJust type in the search bar on the Books page and hit Search. Results filter instantly!"
    ]
  },
  {
    patterns: ['login', 'password', 'credentials', 'admin', 'sign in'],
    replies: [
      "Default admin credentials:\n• Email: <b>admin@library.com</b>\n• Password: <b>admin123</b>\n\nYou can register new accounts with roles: Admin, Librarian, or Member."
    ]
  },
  {
    patterns: ['dark mode', 'light mode', 'theme', 'toggle theme'],
    replies: [
      "Use the <b>toggle switch</b> in the top-right corner of the topbar to switch between dark and light mode. Your preference is saved automatically!"
    ]
  },
  {
    patterns: ['mobile', 'phone', 'responsive', 'tablet'],
    replies: [
      "Yes! LibraryMS is fully responsive 📱\n• On mobile, the sidebar slides in via the ☰ menu\n• All tables scroll horizontally\n• Forms stack vertically\n• Works great on phones and tablets!"
    ]
  },
  {
    patterns: ['deploy', 'github', 'host', 'upload', 'publish'],
    replies: [
      "To deploy on GitHub Pages or a server:\n1. Push code to GitHub\n2. For Render/Railway: add a <b>Procfile</b> with: <code>web: python app.py</code>\n3. Set env vars (SECRET_KEY, etc.)\n4. For GitHub Pages: Flask needs a server — use <b>Render.com</b> (free tier)\n\nWant a Procfile? Just ask!"
    ]
  },
  {
    patterns: ['how many books', 'total books', 'book count', 'inventory'],
    replies: [
      "Check the <b>Dashboard</b> for real-time book counts, or go to the <b>Reports</b> page for full inventory stats including available vs issued copies."
    ]
  },
  {
    patterns: ['delete', 'remove'],
    replies: [
      "To delete a book or member, find them in their respective list pages and click the <b>Delete</b> button (red). You'll get a confirmation before anything is removed."
    ]
  },
  {
    patterns: ['thank', 'thanks', 'great', 'helpful', 'awesome'],
    replies: [
      "Happy to help! 🙌 Let me know if you need anything else.",
      "Anytime! Good luck with your project. 📚",
      "You're welcome! The library is in good hands. 😄"
    ]
  },
  {
    patterns: ['bye', 'goodbye', 'see you', 'exit', 'close'],
    replies: [
      "Goodbye! Come back anytime. 📚",
      "See you! Happy librarian-ing! 👋"
    ]
  }
];

const FALLBACK = [
  "I'm not sure about that, but you can explore the sidebar for all features. Try asking about books, members, fines, or reports!",
  "Hmm, I didn't catch that. Try asking: 'how to issue a book' or 'what is the fine rate?'",
  "I'm still learning! Ask me about adding books, members, transactions, or reports."
];

function getBotReply(input) {
  const text = input.toLowerCase().trim();
  for (const entry of BOT_RESPONSES) {
    if (entry.patterns.some(p => text.includes(p))) {
      const r = entry.replies;
      return r[Math.floor(Math.random() * r.length)];
    }
  }
  return FALLBACK[Math.floor(Math.random() * FALLBACK.length)];
}

// ── DOM ────────────────────────────────────────────────────────────────────

function addMsg(text, who) {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-msg ${who}`;
  div.innerHTML = text.replace(/\n/g, '<br>');
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function sendMessage(text) {
  const input = document.getElementById('chatInput');
  const msg = text || (input ? input.value.trim() : '');
  if (!msg) return;
  addMsg(msg, 'user');
  if (input) input.value = '';
  hideSuggestions();

  setTimeout(() => {
    addMsg(getBotReply(msg), 'bot');
  }, 420);
}

function hideSuggestions() {
  const s = document.getElementById('chatSuggestions');
  if (s) s.style.display = 'none';
}

function toggleChat() {
  const win = document.getElementById('chatWindow');
  const fab = document.getElementById('chatFab');
  const isOpen = win.classList.contains('open');
  win.classList.toggle('open', !isOpen);
  fab.textContent = isOpen ? '💬' : '✕';
  fab.style.borderRadius = isOpen ? '50%' : '14px';
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  if (input) {
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') sendMessage();
    });
  }
});
