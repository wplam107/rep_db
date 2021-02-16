let labels = ["ADD LATER"];
let datasetsLabel = "ADD LATER";
let backgroundColor = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"];
let data = [];

new Chart(document.getElementById('myChart'), {
    type: "bar",
    data: {
        labels: labels,
        datasets: [
            {
                label: "Population (millions)",
                backgroundColor: backgroundColor,
                data: data
            }
        ]
    },
    options: {
        legend: { display: false },
        title: {
            display: true,
            text: "US Representatives (X by Y)"
        },
        responsive: false
    }
});