# 🔍 File Managin — File and Folder Search with Flexible Filters (Python + Tkinter)

**File Managin** is a desktop application for Windows built with Python and Tkinter.  
I originally created it for myself to quickly locate temporary (e.g., `temp`, `cache`) files in the system for manual review and deletion (after assessing the risks, of course).  
Currently, it works as a simple keyword-based search with the ability to open the folder containing the result.  

In the future, I plan to extend the functionality to allow users to **mark reviewed files and folders**, and **delete them in batches**.  
I also intend to add a tab for **searching inside file contents**.  
For example, if you once wrote down a password but forgot where — the app will help you locate the `.txt`, `.docx`, or other document containing keyword "password".

---

## 🚀 Features

- **Keyword Search**:
  - Supports partial and exact match modes.
  - Multiple words allowed (space- or comma-separated).

- **Flexible Size Filter**:
  - Filter files and folders by size (from/to) using units: B, KB, MB, GB, TB.
  - Folder sizes are calculated recursively.

- **Result Sorting**:
  - Sort by name, type, size, or path.
  - Toggle ascending/descending with one click on the column header.

- **Display Filters**:
  - Show only files, only folders, or both.

- **Convenient Navigation**:
  - Double-click opens the containing folder in Explorer.
  - Clean and stylish result table with progress indicator.

- **Multithreaded Processing**:
  - Searching runs in a separate thread, keeping the UI responsive.

---

## 🖼 Interface

The application features a light-themed UI with `Segoe UI` font and intuitive icons:

- 💼 Path selection field  
- 🔤 Keyword input field  
- 🎯 Search mode toggle  
- 📏 Size filter with units  
- 🎛 Display filter panel  
- 📋 Sortable result table  

---

## 🛠 Requirements

- Python 3.8+
- Libraries:
  - `tkinter` (built-in)
  - Also uses built-in modules: `threading`, `os`, `re`, `ttk`, `messagebox`, `filedialog`

---

## ▶️ How to Run

```bash
python main.py
