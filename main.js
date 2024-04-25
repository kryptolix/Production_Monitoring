var dates = ["18.04.2024 10:19","19.04.2024 10:19","22.04.2024 10:20","23.04.2024 10:20","24.04.2024, 10:20"];
var stueckzahlen = [79777,77423,73319,69702,68231];
var wip = 4591;

document.getElementById("stueckzahl").innerHTML = stueckzahlen.slice(-1);
document.getElementById("wip").innerHTML = wip;
document.getElementById("date").innerHTML = dates.slice(-1);

var stueckzahl_array = {
    labels: dates,
    datasets: [
           {
            label: 'Stückzahl',
            borderColor: "red",
            pointColor: "red",
            lineTension: 0,
            fill: false,
            data: stueckzahlen
        }, 
    ]
};
 
document.addEventListener('DOMContentLoaded', function(event) {
    var context = document.getElementById('canvas').getContext('2d');
    var populationChart = new Chart(
        context,
        {
            type: 'line',
            data: stueckzahl_array,
        }
    ); 
});


