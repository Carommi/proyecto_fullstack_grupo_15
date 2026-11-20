(() => {
    const date = document.getElementById("today-date");

    if (date) {
        date.textContent = new Intl.DateTimeFormat("es-CO", {
            weekday: "short",
            day: "numeric",
            month: "short",
            year: "numeric"
        }).format(new Date());
    }

    const money = value => new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        maximumFractionDigits: 0
    }).format(Number(value) || 0);

    const read = key => JSON.parse(localStorage.getItem(key) || "[]");

    const write = (key, data) => {
        localStorage.setItem(key, JSON.stringify(data));
    };

    const id = () => (
        crypto.randomUUID
            ? crypto.randomUUID()
            : String(Date.now() + Math.random())
    );

    const toast = message => {
        const element = document.getElementById("toast");

        if (!element) return;

        element.textContent = message;
        element.classList.add("show");

        clearTimeout(window.toastTimer);

        window.toastTimer = setTimeout(() => {
            element.classList.remove("show");
        }, 2600);
    };

    const api = async (path, options = {}) => {
        const response = await fetch(`${window.APP_CONFIG.API_URL}${path}`, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });

        if (response.status === 204) {
            return null;
        }

        const body = await response.json();

        if (!response.ok) {
            const detail = body.detail
                ? (typeof body.detail === "string"
                    ? body.detail
                    : JSON.stringify(body.detail))
                : `Error ${response.status}`;
            throw new Error(detail);
        }

        return body;
    };

    const store = {
        async getStudents() {
            return window.APP_CONFIG.USE_API
                ? api("/estudiantes")
                : read("gs_students");
        },

        async saveStudent(data, studentId) {
            if (window.APP_CONFIG.USE_API) {
                return studentId
                    ? api(`/estudiantes/${studentId}`, {
                        method: "PUT",
                        body: JSON.stringify(data)
                    })
                    : api("/estudiantes", {
                        method: "POST",
                        body: JSON.stringify(data)
                    });
            }

            const list = read("gs_students");

            if (studentId) {
                const index = list.findIndex(student => student.id === studentId);

                if (index >= 0) {
                    list[index] = { ...list[index], ...data };
                }
            } else {
                list.push({ id: id(), ...data });
            }

            write("gs_students", list);

            return list;
        },

        async deleteStudent(studentId) {
            if (window.APP_CONFIG.USE_API) {
                return api(`/estudiantes/${studentId}`, {
                    method: "DELETE"
                });
            }

            write(
                "gs_students",
                read("gs_students").filter(student => student.id !== studentId)
            );
        },

        async getEnrollments() {
            return window.APP_CONFIG.USE_API
                ? api("/matriculas")
                : read("gs_enrollments");
        },

        async saveEnrollment(data) {
            if (window.APP_CONFIG.USE_API) {
                return api("/matriculas", {
                    method: "POST",
                    body: JSON.stringify(data)
                });
            }

            const list = read("gs_enrollments");

            list.push({ id: id(), ...data });
            write("gs_enrollments", list);

            return list;
        },

        async updateEnrollment(enrollmentId, data) {
            if (window.APP_CONFIG.USE_API) {
                return api(`/matriculas/${enrollmentId}`, {
                    method: "PATCH",
                    body: JSON.stringify(data)
                });
            }

            const list = read("gs_enrollments").map(enrollment => (
                enrollment.id === enrollmentId
                    ? { ...enrollment, ...data }
                    : enrollment
            ));

            write("gs_enrollments", list);
        },

        async deleteEnrollment(enrollmentId) {
            if (window.APP_CONFIG.USE_API) {
                return api(`/matriculas/${enrollmentId}`, {
                    method: "DELETE"
                });
            }

            write(
                "gs_enrollments",
                read("gs_enrollments").filter(enrollment => enrollment.id !== enrollmentId)
            );
        }
    };

    window.GS = {
        money,
        read,
        write,
        toast,
        store
    };

    const page = document.body.dataset.page;

    if (page === "dashboard") {
        loadDashboard();
    }

    async function loadDashboard() {
        try {
            const [students, enrollments] = await Promise.all([
                store.getStudents(),
                store.getEnrollments()
            ]);

            document.getElementById("stat-students").textContent = students.length;
            document.getElementById("stat-enrollments").textContent = enrollments.length;
            document.getElementById("stat-pending").textContent = enrollments.filter(
                enrollment => !enrollment.pagado
            ).length;

            document.getElementById("stat-paid").textContent = money(
                enrollments
                    .filter(enrollment => enrollment.pagado)
                    .reduce(
                        (total, enrollment) => total + Number(enrollment.valor_curso || 0),
                        0
                    )
            );

            const body = document.getElementById("recent-enrollments");
            const recent = [...enrollments].slice(-5).reverse();

            body.innerHTML = recent.length
                ? recent.map(enrollment => `
                    <tr>
                        <td>
                            <span class="student-name">
                                ${esc(enrollment.estudiante_nombre || enrollment.estudiante || "Sin nombre")}
                            </span>
                        </td>
                        <td>
                            ${esc(enrollment.idioma || "")} · ${esc(enrollment.idioma_nivel || "")}
                        </td>
                        <td>${money(enrollment.valor_curso)}</td>
                        <td>${status(enrollment.pagado)}</td>
                    </tr>
                `).join("")
                : `
                    <tr>
                        <td colspan="4" class="empty-cell">
                            Aún no hay matrículas registradas.
                        </td>
                    </tr>
                `;
        } catch (error) {
            console.error(error);
            toast(`No fue posible cargar el panel: ${error.message}`);
        }
    }

    function status(paid) {
        return paid
            ? '<span class="status status-paid">● Pagado</span>'
            : '<span class="status status-pending">● Pendiente</span>';
    }

    function esc(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[character]));
    }

    window.GS.status = status;
    window.GS.esc = esc;
})();