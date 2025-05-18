import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import os
import subprocess

class DockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Developer Docker Setup")
        self.root.geometry("600x700")

        self.java_version = tk.StringVar(value="17")
        self.volume_host = tk.StringVar()
        self.volume_container = tk.StringVar(value="/home/developer/workspace")
        self.docker_network = tk.StringVar(value="bridge")
        self.run_mode = tk.StringVar(value="run")
        self.script_file = tk.StringVar()

        self.use_volume = tk.BooleanVar(value=False)
        self.use_network = tk.BooleanVar(value=False)
        self.use_script = tk.BooleanVar(value=False)

        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="SQL Developer Docker Setup", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Java Settings
        java_frame = ttk.LabelFrame(main_frame, text="Java Settings", padding=10)
        java_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Label(java_frame, text="Select Java Version:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(java_frame, self.java_version, self.java_version.get(), "8", "11", "17", "21").grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(java_frame, text="Run Mode:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.OptionMenu(java_frame, self.run_mode, self.run_mode.get(), "run", "start").grid(row=1, column=1, sticky="ew", padx=5)

        # Volume Settings
        volume_frame = ttk.LabelFrame(main_frame, text="Volume Mount", padding=10)
        volume_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Checkbutton(volume_frame, text="Use volume", variable=self.use_volume).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(volume_frame, text="Host Directory:").grid(row=1, column=0, sticky="w")
        ttk.Entry(volume_frame, textvariable=self.volume_host, width=40).grid(row=1, column=1, sticky="ew")
        ttk.Button(volume_frame, text="Browse", command=self.browse_volume).grid(row=1, column=2, padx=5)

        ttk.Label(volume_frame, text="Container Path:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(volume_frame, textvariable=self.volume_container, width=40).grid(row=2, column=1, columnspan=2, sticky="ew")

        # Network Settings
        network_frame = ttk.LabelFrame(main_frame, text="Network Settings", padding=10)
        network_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Checkbutton(network_frame, text="Use custom network", variable=self.use_network).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(network_frame, text="Network Name:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(network_frame, textvariable=self.docker_network, width=40).grid(row=1, column=1, columnspan=2, sticky="ew")

        # Script Settings
        script_frame = ttk.LabelFrame(main_frame, text="Startup Script", padding=10)
        script_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Checkbutton(script_frame, text="Use startup script", variable=self.use_script).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(script_frame, text="Script File:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(script_frame, textvariable=self.script_file, width=40).grid(row=1, column=1, sticky="ew")
        ttk.Button(script_frame, text="Browse", command=self.browse_script_file).grid(row=1, column=2, padx=5)

        # Action Buttons
        button_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        button_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(button_frame, text="Create Dockerfile", command=self.create_dockerfile).grid(row=0, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Set X11 Permissions", command=self.set_x11_permissions).grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Build Docker Image", command=self.build_docker_image).grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Run Docker Container", command=self.run_docker_container).grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        
        ttk.Button(button_frame, text="Stop and Remove Container", command=self.stop_and_remove_container).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        for i in range(3):
            main_frame.columnconfigure(i, weight=1)

    # Установка volume
    def browse_volume(self):
        path = filedialog.askdirectory()
        if path:
            self.volume_host.set(path)

    # Установка начального скрипта
    def browse_script_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.sh"), ("All Files", "*.*")])
        if path:
            self.script_file.set(path)

    # Генерация Докерфайла
    def create_dockerfile(self):
        java_version = self.java_version.get()
        uid = os.getuid()

        script_content = ""
        script_file = self.script_file.get().strip()
        if script_file:
            with open(script_file, 'r') as file:
                script_content = file.read()

        dockerfile_content = f"""
FROM debian:bookworm-slim

ARG uid={uid}

RUN test -n "${{uid}}" || (echo "docker build-arg uid must be set" && false)

RUN apt-get update && \\
    apt-get install -y \\
    openjdk-{java_version}-jdk \\
    wget \\
    libxext6 \\
    libxrender1 \\
    libxtst6 \\
    libxi6 \\
    libgtk-3-0 \\
    libdbus-glib-1-2 \\
    libasound2 \\
    rpm2cpio \\
    cpio \\
    && rm -rf /var/lib/apt/lists/*
    
RUN wget --no-check-certificate --quiet \\
    "https://download.oracle.com/otn_software/java/sqldeveloper/sqldeveloper-24.3.1-347.1826.noarch.rpm" -O /tmp/sqldeveloper.rpm

RUN rpm2cpio /tmp/sqldeveloper.rpm | cpio -idmv && \\
    rm /tmp/sqldeveloper.rpm

ENV JAVA_HOME=/usr/lib/jvm/java-{java_version}-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

RUN ln -s /opt/instantclient/sqlplus /usr/bin/sqlplus64
"""

        # Добавление скрипта, только если флаг активен
        if self.use_script.get():
            dockerfile_content += """
COPY script.sh /script.sh
RUN chmod +x /script.sh
ENTRYPOINT ["/bin/bash", "-c", "/script.sh && /opt/sqldeveloper/sqldeveloper.sh"]
"""
        else:
            dockerfile_content += """
ENTRYPOINT ["/opt/sqldeveloper/sqldeveloper.sh"]
        """
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Если начального скрипта нет
        if script_content:
            with open("script.sh", "w") as script_file:
                script_file.write(script_content)

        messagebox.showinfo("Success", "Dockerfile and script created successfully!")

    def set_x11_permissions(self):
        try:
            subprocess.run(["xhost", "-local:root"], check=True)
            messagebox.showinfo("Success", "X11 permissions set successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to set X11 permissions. Make sure X11 server is running.")

    def build_docker_image(self):
        try:
            image_name = "sqldeveloper:debian-buster"
            
            # Удаление старого образа, если существует
            subprocess.run(f"docker rmi -f {image_name}", shell=True, check=False)

            uid = os.getuid()
            subprocess.run(f"docker build -t {image_name} --build-arg uid={uid} .", shell=True, check=True)
            messagebox.showinfo("Success", "Docker image built successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to build Docker image.")


    def run_docker_container(self):
        try:
            mode = self.run_mode.get()

            if mode == "start":
                command = "sudo docker start -ai sqldeveloper-container"
            else:
                display = os.environ.get("DISPLAY", ":0")
                xauth = os.environ.get("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

                # Volume
                volume_option = ""
                if self.use_volume.get():
                    host_path = self.volume_host.get().strip()
                    container_path = self.volume_container.get().strip()
                    if host_path and container_path:
                        volume_option = f'-v "{host_path}":"{container_path}"'

                # Network
                network_option = ""
                if self.use_network.get():
                    network = self.docker_network.get().strip()
                    if network:
                        network_option = f"--network {network}"

                # Script mount
                script_option = ""
                if self.use_script.get():
                    script_path = self.script_file.get().strip()
                    if script_path:
                        script_option = f'-v "{script_path}":/script.sh'

                command = f"""
                    sudo docker run -it \
                        --name sqldeveloper-container \
                        -e DISPLAY={display} \
                        -e XAUTHORITY={xauth} \
                        -v /tmp/.X11-unix:/tmp/.X11-unix \
                        -v {xauth}:{xauth} \
                        {volume_option} \
                        {network_option} \
                        {script_option} \
                        sqldeveloper:debian-buster
                    """.replace("\n", " ").strip()

            print("Running command:", command)
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to run Docker container.")

    # Остановка и удаление контейнера
    def stop_and_remove_container(self):
        try:
            subprocess.run("sudo docker stop sqldeveloper-container", shell=True, check=True)
            subprocess.run("sudo docker rm sqldeveloper-container", shell=True, check=True)
            messagebox.showinfo("Success", "Container stopped and removed successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to stop and remove the container. Ensure the container exists.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DockerApp(root)
    root.mainloop()