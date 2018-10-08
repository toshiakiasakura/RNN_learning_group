console.log("Hello World!");
var mass = +process.argv[2];
var height = +process.argv[3];
BMI = mass/Math.pow(height,2);
console.log(BMI);