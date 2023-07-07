let chart;

// Function to send toggle state to the server

console.log("hi");
// WebSocket event listener
const socket = new WebSocket("ws://localhost:8000/ws?client=viewer");

function sendToggleState(){
    var switch1 = document.getElementById("switch1").checked;
    var switch2 = document.getElementById("switch2").checked;
    var data = JSON.stringify({"switch1": switch1, "switch2": switch2});
    socket.send(data);
}

window.addEventListener("load", function () {
    // Create the initial chart

    const chartCanvas = document.getElementById("chart");
    chart = new Chart(chartCanvas, {
        type: "line",
        data: {
            labels: [], // Set initial labels
            datasets: [{
                label: "Dynamic Chart",
                data: [], // Set initial data
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: "Time"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: "Value"
                    }
                }
            }
        }
    });


    socket.addEventListener("message", function (event) {
        console.log("Message from server: " + event.data);
        var val = parseFloat(event.data);
        // Process the received data and update the chart
        updateChart(val);
    });

    socket.addEventListener("connect", function (event) {
        console.log("connected");
        socket.send("20")
    })
    // Retrieve initial data from the server using AJAX or WebSocket
    // Update the chart with the received data
});

function updateChart(data) {
    // Parse the received data
    // const { labels, values } = JSON.parse(data);
    var time = new Date().toLocaleTimeString();
    // Update the chart data
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(data);

    // Update the chart
    chart.update();
}
