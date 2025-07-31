import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
from tkinter.font import Font


class FileSearchApp:
	def __init__(self, root):
		self.root = root
		self.root.title("🔍 Поиск файлов и папок")
		self.root.geometry("1200x750")
		self.root.minsize(1000, 600)
		
		# Настройка стилей
		self.setup_styles()
		
		# Переменные
		self.search_path = tk.StringVar()
		self.keyword = tk.StringVar()
		self.search_mode = tk.StringVar(value="вхождение")
		self.show_files = tk.BooleanVar(value=True)
		self.show_folders = tk.BooleanVar(value=True)
		self.size_filter_enabled = tk.BooleanVar(value=False)
		self.size_from = tk.StringVar(value="0")
		self.size_to = tk.StringVar(value="")
		self.size_unit_from = tk.StringVar(value="B")
		self.size_unit_to = tk.StringVar(value="B")
		self.search_thread = None
		self.is_searching = False
		self.all_results = []
		self.sort_column = None
		self.sort_reverse = False
		
		self.create_widgets()
		self.update_size_filter_state()  # Инициализация состояния фильтра
	
	def setup_styles(self):
		"""Настройка стилей для более красивого интерфейса"""
		style = ttk.Style()
		
		# Цветовая схема
		bg_color = "#f0f0f0"
		accent_color = "#4a90e2"
		button_color = "#3498db"
		button_hover_color = "#2980b9"
		
		# Настройка стилей
		style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), foreground="#2c3e50")
		style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground="#34495e")
		style.configure("TButton", font=("Segoe UI", 9), padding=4)
		style.configure("Accent.TButton", background=button_color, foreground="white")
		style.map("Accent.TButton", background=[("active", button_hover_color)])
		
		# Стиль для Treeview
		style.configure("Treeview", font=("Segoe UI", 9), rowheight=22)
		style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
		
		# Цвета для результатов
		self.root.configure(bg=bg_color)
	
	def create_widgets(self):
		# Главный контейнер
		main_container = tk.Frame(self.root, bg="#f0f0f0")
		main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Заголовок
		title_frame = tk.Frame(main_container, bg="#f0f0f0")
		title_frame.pack(fill=tk.X, pady=(0, 10))
		
		title_label = ttk.Label(title_frame, text="🔍 Поиск файлов и папок", style="Title.TLabel")
		title_label.pack(side=tk.LEFT)
		
		# Панель поиска (компактная)
		search_panel = tk.LabelFrame(main_container, text=" 🔍 Параметры поиска ",
									 font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2c3e50")
		search_panel.pack(fill=tk.X, pady=(0, 10))
		
		# Содержимое панели поиска
		search_content = tk.Frame(search_panel, bg="#f8f9fa")
		search_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Первая строка - путь и ключевые слова
		row1 = tk.Frame(search_content, bg="#f8f9fa")
		row1.pack(fill=tk.X, pady=2)
		
		# Путь
		ttk.Label(row1, text="📁 Путь:", style="Header.TLabel").pack(side=tk.LEFT)
		ttk.Entry(row1, textvariable=self.search_path, font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True,
																				  padx=(5, 5))
		ttk.Button(row1, text="Обзор", command=self.browse_folder, style="Accent.TButton", width=8).pack(side=tk.RIGHT)
		
		# Вторая строка - ключевые слова
		row2 = tk.Frame(search_content, bg="#f8f9fa")
		row2.pack(fill=tk.X, pady=2)
		
		ttk.Label(row2, text="🔤 Ключевые слова:", style="Header.TLabel").pack(side=tk.LEFT)
		ttk.Entry(row2, textvariable=self.keyword, font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True,
																			  padx=(5, 0))
		
		# Третья строка - режим поиска и фильтр размеров
		row3 = tk.Frame(search_content, bg="#f8f9fa")
		row3.pack(fill=tk.X, pady=2)
		
		# Режим поиска
		ttk.Label(row3, text="🎯 Режим:", style="Header.TLabel").pack(side=tk.LEFT)
		ttk.Radiobutton(row3, text="Вхождение", variable=self.search_mode, value="вхождение").pack(side=tk.LEFT,
																								   padx=(5, 0))
		ttk.Radiobutton(row3, text="Точное", variable=self.search_mode, value="точное").pack(side=tk.LEFT,
																							 padx=(10, 15))
		
		# Фильтр размеров
		ttk.Checkbutton(row3, variable=self.size_filter_enabled, command=self.update_size_filter_state).pack(
			side=tk.LEFT)
		ttk.Label(row3, text="📏 Размер:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(5, 5))
		
		ttk.Label(row3, text="от:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
		self.size_from_entry = ttk.Entry(row3, textvariable=self.size_from, width=6, font=("Segoe UI", 9))
		self.size_from_entry.pack(side=tk.LEFT, padx=(2, 2))
		
		unit_options = ["B", "KB", "MB", "GB", "TB"]
		self.unit_combo_from = ttk.Combobox(row3, textvariable=self.size_unit_from,
											values=unit_options, width=4, state="readonly", font=("Segoe UI", 9))
		self.unit_combo_from.pack(side=tk.LEFT, padx=(0, 10))
		self.unit_combo_from.set("B")
		
		ttk.Label(row3, text="до:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
		self.size_to_entry = ttk.Entry(row3, textvariable=self.size_to, width=6, font=("Segoe UI", 9))
		self.size_to_entry.pack(side=tk.LEFT, padx=(2, 2))
		
		self.unit_combo_to = ttk.Combobox(row3, textvariable=self.size_unit_to,
										  values=unit_options, width=4, state="readonly", font=("Segoe UI", 9))
		self.unit_combo_to.pack(side=tk.LEFT, padx=(0, 0))
		self.unit_combo_to.set("B")
		
		# Четвертая строка - кнопки и прогресс
		row4 = tk.Frame(search_content, bg="#f8f9fa")
		row4.pack(fill=tk.X, pady=(5, 0))
		
		self.search_button = ttk.Button(row4, text="🚀 Найти", command=self.start_search,
										style="Accent.TButton")
		self.search_button.pack(side=tk.LEFT)
		
		self.stop_button = ttk.Button(row4, text="⏹ Стоп", command=self.stop_search,
									  state=tk.DISABLED)
		self.stop_button.pack(side=tk.LEFT, padx=(5, 10))
		
		self.progress = ttk.Progressbar(row4, mode='indeterminate')
		self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)
		self.progress_label = ttk.Label(row4, text="", font=("Segoe UI", 9), foreground="#7f8c8d")
		self.progress_label.pack(side=tk.RIGHT, padx=(0, 10))
		
		# Панель фильтров и результатов
		results_panel = tk.Frame(main_container, bg="#f0f0f0")
		results_panel.pack(fill=tk.BOTH, expand=True)
		
		# Фильтры отображения
		filter_frame = tk.LabelFrame(results_panel, text=" 🎛 Фильтры отображения ",
									 font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2c3e50")
		filter_frame.pack(fill=tk.X, pady=(0, 10))
		
		filter_content = tk.Frame(filter_frame, bg="#f8f9fa")
		filter_content.pack(fill=tk.X, padx=10, pady=5)
		
		ttk.Checkbutton(filter_content, variable=self.show_files, command=self.apply_filters).pack(side=tk.LEFT)
		ttk.Label(filter_content, text="Файлы", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(2, 15))
		
		ttk.Checkbutton(filter_content, variable=self.show_folders, command=self.apply_filters).pack(side=tk.LEFT)
		ttk.Label(filter_content, text="Папки", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(2, 15))
		
		# Статистика
		self.stats_label = ttk.Label(filter_content, text="Найдено: 0 элементов",
									 font=("Segoe UI", 9), foreground="#7f8c8d")
		self.stats_label.pack(side=tk.RIGHT)
		
		# Таблица результатов
		self.create_table(results_panel)
	
	def update_size_filter_state(self):
		"""Обновление состояния элементов фильтра размеров"""
		state = "normal" if self.size_filter_enabled.get() else "disabled"
		self.size_from_entry.config(state=state)
		self.size_to_entry.config(state=state)
		self.unit_combo_from.config(state=state)
		self.unit_combo_to.config(state=state)
	
	def create_table(self, parent):
		# Фрейм для таблицы
		table_frame = tk.LabelFrame(parent, text=" 📋 Результаты поиска ",
									font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2c3e50")
		table_frame.pack(fill=tk.BOTH, expand=True)
		
		# Внутренний фрейм
		inner_frame = tk.Frame(table_frame, bg="#f8f9fa")
		inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
		
		# Создаем Treeview
		columns = ('name', 'type', 'size', 'path')
		self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', height=15)
		
		# Определяем заголовки с возможностью сортировки
		self.tree.heading('name', text='📋 Название', command=lambda: self.sort_column_data('name'))
		self.tree.heading('type', text='🏷 Тип', command=lambda: self.sort_column_data('type'))
		self.tree.heading('size', text='📊 Размер', command=lambda: self.sort_column_data('size'))
		self.tree.heading('path', text='📍 Путь', command=lambda: self.sort_column_data('path'))
		
		# Устанавливаем ширину колонок
		self.tree.column('name', width=250, minwidth=150)
		self.tree.column('type', width=80, minwidth=80)
		self.tree.column('size', width=100, minwidth=100)
		self.tree.column('path', width=450, minwidth=300)
		
		# Скроллбары
		v_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.tree.yview)
		h_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
		self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
		
		# Размещаем элементы
		self.tree.grid(row=0, column=0, sticky='nsew')
		v_scrollbar.grid(row=0, column=1, sticky='ns')
		h_scrollbar.grid(row=1, column=0, sticky='ew')
		
		inner_frame.grid_rowconfigure(0, weight=1)
		inner_frame.grid_columnconfigure(0, weight=1)
		
		# Обработчик клика по таблице
		self.tree.bind('<Double-1>', self.on_tree_double_click)
		self.tree.bind('<Button-1>', self.on_tree_click)
		
		# Теги для стилизации строк
		self.tree.tag_configure('file', background='#ffffff')
		self.tree.tag_configure('folder', background='#f8f9fa')
	
	def browse_folder(self):
		folder = filedialog.askdirectory()
		if folder:
			self.search_path.set(folder)
	
	def format_size(self, size_bytes):
		"""Форматирование размера файла"""
		if size_bytes == 0:
			return "0 B"
		if size_bytes == -1:
			return "Папка"
		
		size_names = ["B", "KB", "MB", "GB", "TB"]
		i = 0
		while size_bytes >= 1024 and i < len(size_names) - 1:
			size_bytes /= 1024.0
			i += 1
		return f"{size_bytes:.1f} {size_names[i]}"
	
	def convert_to_bytes(self, size_value, unit):
		"""Конвертация значения в байты"""
		try:
			size = float(size_value)
			units = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3, "TB": 1024 ** 4}
			return size * units.get(unit, 1)
		except (ValueError, TypeError):
			return 0
	
	def get_directory_size(self, path):
		"""Рекурсивное получение размера папки"""
		total_size = 0
		try:
			for dirpath, dirnames, filenames in os.walk(path):
				for filename in filenames:
					filepath = os.path.join(dirpath, filename)
					try:
						total_size += os.path.getsize(filepath)
					except (OSError, PermissionError):
						continue
				if not self.is_searching:
					return -1
		except (OSError, PermissionError):
			return -1
		return total_size
	
	def get_file_size(self, path):
		"""Получение размера файла или папки"""
		try:
			if os.path.isfile(path):
				return os.path.getsize(path)
			elif os.path.isdir(path):
				return self.get_directory_size(path)
			else:
				return 0
		except (OSError, PermissionError):
			return -1
	
	def parse_keywords(self):
		"""Парсинг ключевых слов из строки"""
		keywords_text = self.keyword.get().strip()
		if not keywords_text:
			return []
		
		keywords = re.split(r'[,\s]+', keywords_text)
		keywords = [kw.strip() for kw in keywords if kw.strip()]
		return keywords
	
	def matches_keyword(self, name):
		"""Проверка соответствия ключевому слову"""
		keywords = self.parse_keywords()
		if not keywords:
			return True
		
		for keyword in keywords:
			if self.search_mode.get() == "точное":
				if name.lower() == keyword.lower():
					return True
			else:
				if keyword.lower() in name.lower():
					return True
		return False
	
	def matches_size_filter(self, size_bytes):
		"""Проверка соответствия фильтру размеров"""
		if not self.size_filter_enabled.get():
			return True
		
		if size_bytes == -1:
			return True
		
		try:
			if self.size_from.get().strip():
				size_from_bytes = self.convert_to_bytes(self.size_from.get().strip(), self.size_unit_from.get())
				if size_bytes < size_from_bytes:
					return False
			
			if self.size_to.get().strip():
				size_to_bytes = self.convert_to_bytes(self.size_to.get().strip(), self.size_unit_to.get())
				if size_bytes > size_to_bytes:
					return False
			
			return True
		except ValueError:
			return True
	
	def search_files_and_folders(self):
		"""Основная функция поиска"""
		search_path = self.search_path.get()
		keywords = self.parse_keywords()
		
		if not search_path:
			self.root.after(0, lambda: messagebox.showwarning("Предупреждение", "Укажите путь для поиска!"))
			self.search_finished()
			return
		
		if not keywords:
			self.root.after(0, lambda: messagebox.showwarning("Предупреждение", "Укажите хотя бы одно ключевое слово!"))
			self.search_finished()
			return
		
		if not os.path.exists(search_path):
			self.root.after(0, lambda: messagebox.showerror("Ошибка", "Указанный путь не существует!"))
			self.search_finished()
			return
		
		self.all_results = []
		self.root.after(0, lambda: [self.tree.delete(item) for item in self.tree.get_children()])
		self.root.after(0, lambda: self.stats_label.config(text="Поиск..."))
		
		found_count = 0
		
		try:
			for root, dirs, files in os.walk(search_path):
				if not self.is_searching:
					break
				
				for dir_name in dirs:
					if not self.is_searching:
						break
					if self.matches_keyword(dir_name):
						full_path = os.path.join(root, dir_name)
						size = self.get_file_size(full_path)
						if self.size_filter_enabled.get() and not self.matches_size_filter(size):
							continue
						size_formatted = self.format_size(size) if size != -1 else "Папка"
						result_data = {
							'name': dir_name,
							'type': 'Папка',
							'size': size_formatted,
							'size_value': size,
							'path': full_path
						}
						self.all_results.append(result_data)
						found_count += 1
						if found_count % 10 == 0:
							self.root.after(0, lambda c=found_count: self.stats_label.config(
								text=f"Найдено: {c} элементов"))
							self.root.update_idletasks()
				
				for file_name in files:
					if not self.is_searching:
						break
					if self.matches_keyword(file_name):
						full_path = os.path.join(root, file_name)
						size = self.get_file_size(full_path)
						if not self.matches_size_filter(size):
							continue
						size_formatted = self.format_size(size) if size != -1 else "0 B"
						result_data = {
							'name': file_name,
							'type': 'Файл',
							'size': size_formatted,
							'size_value': size,
							'path': full_path
						}
						self.all_results.append(result_data)
						found_count += 1
						if found_count % 10 == 0:
							self.root.after(0, lambda c=found_count: self.stats_label.config(
								text=f"Найдено: {c} элементов"))
							self.root.update_idletasks()
		
		except Exception as e:
			self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}"))
		
		self.root.after(0, self.apply_filters)
		self.root.after(0, lambda: self.stats_label.config(text=f"Найдено: {found_count} элементов"))
		
		self.search_finished()
		self.root.after(0, lambda: messagebox.showinfo("Поиск завершен", f"Найдено элементов: {found_count}"))
	
	def apply_filters(self):
		"""Применение фильтров отображения"""
		for item in self.tree.get_children():
			self.tree.delete(item)
		
		filtered_results = []
		for result in self.all_results:
			if result['type'] == 'Файл' and not self.show_files.get():
				continue
			if result['type'] == 'Папка' and not self.show_folders.get():
				continue
			filtered_results.append(result)
		
		for i, result in enumerate(filtered_results):
			tag = 'folder' if result['type'] == 'Папка' else 'file'
			self.tree.insert('', tk.END, values=(
				result['name'],
				result['type'],
				result['size'],
				result['path']
			), tags=(tag,))
	
	def sort_column_data(self, col):
		"""Сортировка данных по столбцу"""
		if self.sort_column == col:
			self.sort_reverse = not self.sort_reverse
		else:
			self.sort_reverse = False
		self.sort_column = col
		
		if col == 'size':
			self.all_results.sort(key=lambda x: (x['size_value'], x['type']), reverse=self.sort_reverse)
		else:
			self.all_results.sort(key=lambda x: x[col].lower(), reverse=self.sort_reverse)
		
		self.apply_filters()
	
	def start_search(self):
		"""Запуск поиска в отдельном потоке"""
		if self.is_searching:
			return
		
		self.is_searching = True
		self.search_button.config(state=tk.DISABLED)
		self.stop_button.config(state=tk.NORMAL)
		self.progress.start()
		
		self.search_thread = threading.Thread(target=self.search_files_and_folders)
		self.search_thread.daemon = True
		self.search_thread.start()
	
	def stop_search(self):
		"""Остановка поиска"""
		self.is_searching = False
		self.search_finished()
	
	def search_finished(self):
		"""Завершение поиска"""
		self.is_searching = False
		self.search_button.config(state=tk.NORMAL)
		self.stop_button.config(state=tk.DISABLED)
		self.progress.stop()
	
	def on_tree_double_click(self, event):
		"""Обработчик двойного клика по таблице"""
		self.open_selected_item()
	
	def on_tree_click(self, event):
		"""Обработчик клика по таблице"""
		region = self.tree.identify("region", event.x, event.y)
		if region == "heading":
			column = self.tree.identify_column(event.x)
			col_map = {'#1': 'name', '#2': 'type', '#3': 'size', '#4': 'path'}
			if column in col_map:
				self.sort_column_data(col_map[column])
	
	def open_selected_item(self):
		"""Открытие выбранного элемента"""
		selection = self.tree.selection()
		if selection:
			item = selection[0]
			path = self.tree.item(item, 'values')[3]
			if os.path.exists(path):
				try:
					containing_folder = os.path.dirname(path)
					os.startfile(containing_folder)
				except Exception as e:
					messagebox.showerror("Ошибка", f"Не удалось открыть путь: {str(e)}")
			else:
				messagebox.showwarning("Предупреждение", "Файл или папка не существует")


def main():
	root = tk.Tk()
	app = FileSearchApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
