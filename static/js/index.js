document.addEventListener('DOMContentLoaded', () => {
    alert('Hello, World!');
    fetchServers();
});

function fetchServers() {
    fetch('http://127.0.0.1:5000/servers')
        .then(response => response.json())
        .then(data => {
            displayServers(data);
        })
        .catch(error => console.error('Error fetching servers:', error));
}

function displayServers(servers) {
    const container = document.getElementById('servers-container');
    if (servers.length === 0) {
        container.innerHTML = '<p>No servers found.</p>';
        return;
    }

    const table = document.createElement('table');
    table.innerHTML = `
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>IP Address</th>
            <th>Status</th>
        </tr>
    `;

    servers.forEach(server => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${server[0]}</td>
            <td>${server[1]}</td>
            <td>${server[2]}</td>
            <td>${server[3]}</td>
        `;
        table.appendChild(row);
    });

    container.appendChild(table);
}