import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess

class DockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Developer Docker Setup")
        self.root.geometry("500x650")

        self.java_version = tk.StringVar(value="17")
        self.volume_host = tk.StringVar()
        self.volume_container = tk.StringVar(value="/home/developer/workspace")
        self.docker_network = tk.StringVar(value="bridge")  # Default network
        self.run_mode = tk.StringVar(value="run")  # New: run or start
        self.script_file = tk.StringVar()  # File path for the script

        # Java version
        tk.Label(root, text="Select Java Version").pack(pady=5)
        tk.OptionMenu(root, self.java_version, "8", "11", "17", "21").pack(pady=5)

        # Volume selection
        tk.Label(root, text="Select host directory to mount as volume").pack(pady=5)
        tk.Entry(root, textvariable=self.volume_host, width=50).pack(pady=2)
        tk.Button(root, text="Browse", command=self.browse_volume).pack(pady=2)

        tk.Label(root, text="Container path for the volume").pack(pady=2)
        tk.Entry(root, textvariable=self.volume_container, width=50).pack(pady=2)

        # Docker network
        tk.Label(root, text="Docker network").pack(pady=5)
        tk.Entry(root, textvariable=self.docker_network, width=50).pack(pady=2)

        # Run mode
        tk.Label(root, text="Choose Run Mode").pack(pady=5)
        tk.OptionMenu(root, self.run_mode, "run", "start").pack(pady=2)

        # File input for script
        tk.Label(root, text="Select script file for non-interactive mode").pack(pady=5)
        tk.Entry(root, textvariable=self.script_file, width=50).pack(pady=2)
        tk.Button(root, text="Browse", command=self.browse_script_file).pack(pady=2)

        # Buttons
        tk.Button(root, text="Create Dockerfile", command=self.create_dockerfile).pack(pady=10)
        tk.Button(root, text="Set X11 Permissions", command=self.set_x11_permissions).pack(pady=5)
        tk.Button(root, text="Build Docker Image", command=self.build_docker_image).pack(pady=5)
        tk.Button(root, text="Run Docker Container", command=self.run_docker_container).pack(pady=10)

    def browse_volume(self):
        path = filedialog.askdirectory()
        if path:
            self.volume_host.set(path)

    def browse_script_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.sh"), ("All Files", "*.*")])
        if path:
            self.script_file.set(path)

    def create_dockerfile(self):
        java_version = self.java_version.get()
        uid = os.getuid()

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

CMD ["/usr/sqldeveloper/opt/sqldeveloper/sqldeveloper.sh"]
"""
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
        messagebox.showinfo("Success", "Dockerfile created successfully!")

    def set_x11_permissions(self):
        try:
            subprocess.run(["xhost", "-local:root"], check=True)
            messagebox.showinfo("Success", "X11 permissions set successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to set X11 permissions. Make sure X11 server is running.")

    def build_docker_image(self):
        try:
            uid = os.getuid()
            subprocess.run(f"docker build -t sqldeveloper:debian-buster --build-arg uid={uid} .", shell=True, check=True)
            messagebox.showinfo("Success", "Docker image built successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to build Docker image.")

    def run_docker_container(self):
        try:
            mode = self.run_mode.get()
            script_file = self.script_file.get().strip()  # Get the script file path

            # If there's a script file, add it to the command
            script_option = ""
            if script_file:
                script_option = f"-v {script_file}:/script.sh"  # Mount the script file into the container

            if mode == "start":
                command = "sudo docker start -ai sqldeveloper-container"
            else:
                display = os.environ.get("DISPLAY", ":1")
                volume_option = ""
                host_path = self.volume_host.get().strip()
                container_path = self.volume_container.get().strip()
                if host_path and container_path:
                    volume_option = f'-v "{host_path}":"{container_path}"'

                network = self.docker_network.get().strip()
                network_option = f"--network {network}" if network else ""

                command = f"""
                    sudo docker run -it \
                        --name sqldeveloper-container \
                        -e DISPLAY={display} \
                        -v /tmp/.X11-unix:/tmp/.X11-unix \
                        {volume_option} \
                        {network_option} \
                        {script_option} \
                        sqldeveloper:debian-buster /bin/bash -c "bash /script.sh && /usr/sqldeveloper/opt/sqldeveloper/sqldeveloper.sh"
                    """.replace("\n", " ").strip()

            print("Running command:", command)
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to run Docker container.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DockerApp(root)
    root.mainloop()
