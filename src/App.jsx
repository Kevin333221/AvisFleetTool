import './App.css'
import * as XLSX from 'xlsx/xlsx.mjs';
import { useState, useEffect } from 'react';
import logo from "../public/Avis.png"

export default function App() {
  
  const [data, setData] = useState([]);
  const [cars, setCars] = useState([]);
  const [search, setSearch] = useState("");
  const [owner, setOwner] = useState("64442");
  const [stations, setStations] = useState([]);

  useEffect(() => {
    get_stations();
  }, [owner, data]);

  function dateToExcelSerialNumber(date) {
    const excelEpoch = new Date(Date.UTC(1900, 1, 1)); // January 1, 1900
    const millisecondsPerDay = 24 * 60 * 60 * 1000;

    // Calculate the difference in milliseconds between the target date and Excel epoch
    const millisecondsDifference = date.getTime() - excelEpoch.getTime();

    // Convert milliseconds to days
    const daysDifference = millisecondsDifference / millisecondsPerDay;

    // Add 1 because Excel's epoch starts on January 0, 1900 (Excel considers January 0, 1900, as January 1, 1900)
    // Round up
    return Math.ceil(daysDifference) + 1;
  }

  function sortCars(cars, sortDirection, sortingType) {
    const sortedCars = [...cars]; // Create a new array

    if (sortDirection === "ASC") {

      sortedCars.sort((a, b) => {
        if (a[sortingType] < b[sortingType]) {
          return -1;
        }
        if (a[sortingType] > b[sortingType]) {
          return 1;
        }
        if (a[sortingType] === b[sortingType]) {
          return 0;
        }
      });
    } else if (sortDirection === "DESC") {
      sortedCars.sort((a, b) => {
        if (a[sortingType] > b[sortingType]) {
          return -1;
        }
        if (a[sortingType] < b[sortingType]) {
          return 1;
        }
        if (a[sortingType] === b[sortingType]) {
          return 0;
        }
      });
    }
    setCars(sortedCars);
  }

  function fetch_data() {
    const baseDate = new Date(1900, 0, 0);
    const input = document.getElementById('file-input'); // Assuming your input element has id="file-input"
  
    if (!input.files || input.files.length === 0) {
      console.error('No file selected');
      return;
    }
  
    const file = input.files[0]; // Get the first selected file
    const reader = new FileReader();

    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { cellDates: true });

      const sheet_name_list = workbook.SheetNames;
      const xlData = XLSX.utils.sheet_to_json(workbook.Sheets[sheet_name_list[0]]);

      xlData.pop(); // Remove the last row in the sheet

      setData(xlData);

      let cars = [];
      for (let i = 0; i < xlData.length; i++) {

        // Check if the json has the "Checkin Datetime" key
        if (xlData[i]["Checkin Datetime"] !== undefined && xlData[i].hasOwnProperty("Checkin Datetime") && typeof xlData[i]["Checkin Datetime"] === "number") {          
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData[i]["Checkin Datetime"]);
          xlData[i]["Checkin Datetime"] = newDate;
        }

        // Fix conversion of "Vehicle Mileage" to number
        if (typeof xlData[i]["Vehicle Mileage"] !== "number") {
          xlData[i]["Vehicle Mileage"] = Number(dateToExcelSerialNumber(xlData[i]["Vehicle Mileage"]));
        }
        cars.push(xlData[i]);
      }

      setCars(cars);
      sortCars(cars, "ASC", "Car Group");
      get_stations()
    }

    reader.readAsArrayBuffer(file);
  }

  function check_owner(car, owner) {
    return car["Fleet Owner Code"] === owner || owner === "All" || owner === "";
  }

  function get_stations() {
    let stations = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (check_owner(car, owner)) {
        if (stations.indexOf(car["Location Due Mne"]) === -1) {
          stations.push(car["Location Due Mne"]);
        }
        if (stations.indexOf(car["Current Location Mne"]) === -1) {
          stations.push(car["Current Location Mne"]);
        }
      }
    }

    stations.sort();

    {/* If station is "Unknow" delete it */}
    if (stations.indexOf("Unknow") !== -1) {
      stations.splice(stations.indexOf("Unknow"), 1);
    }

    setStations(stations);
  }

  function fix_duplicate_status(status) {
      
      let status_array = status.split(' ');
      let first_status = status_array[0];
      let new_status = first_status + " ";
  
      for (let i = 1; i < status_array.length; i++) {
        if (first_status === status_array[i]) {
          return new_status
        } else {
          new_status += status_array[i] + " ";
        }
      }
      return status;
  }

  function get_serivce() {

    let cars = [];

    const Service_offset = 700;

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      const current_mileage = Number(car["Vehicle Mileage"]) + Service_offset;
      const key_mileage = Number(car["Ignition Key"].substring(3, 8));

      if (current_mileage > key_mileage) {
        if (check_owner(car, owner)) {
          if (car["STATUS3"].indexOf("BB") === -1 && car["Checkout Location Mne"] !== "E9Z" && car["Checkout Location Mne"] !== "R4S") {
            cars.push(data[i]);
          }
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_overdue_RA() {

    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (length !== "NaN") {

        let curDate = new Date().getDate();
        let curMonth = new Date().getMonth();
        let curYear = new Date().getFullYear();

        if (car["Checkin Datetime"] === undefined) {
          continue;
        }

        let checkinDate = car["Checkin Datetime"].getDate();
        let checkinMonth = car["Checkin Datetime"].getMonth();
        let checkinYear = car["Checkin Datetime"].getFullYear();
        
        if (car["Fleet Owner Code"] === owner) {
          if (car["Rental Agreement Num"].length === 10 || car["Rental Agreement Num"].length === 9) {
            if (curYear > checkinYear || (curYear === checkinYear && curMonth > checkinMonth) || (curYear === checkinYear && curMonth === checkinMonth && curDate > checkinDate)) {
              cars.push(data[i]);
            }
          }
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_buy_back() {
    let cars = [];

    const BB_number_offset = 5000;

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Fleet Owner Code"] === owner) {
        if (car["STATUS3"].indexOf("BB") !== -1 || ((car["Ignition Key"].substring(3, 8) >= Number(car["Ignition Key"].substring(0, 2))*1000) && car["Vehicle Mileage"] + BB_number_offset >= (Number(car["Ignition Key"].substring(0, 2))*1000).toString())) {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_all(station) {

    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (owner.toUpperCase() === "ALL" || owner === "") {
        if (station === "All") {
          cars.push(data[i]);
        }
      } else if (car["Fleet Owner Code"] === owner) {
        if (station === "All") {
            cars.push(data[i]);
        } else {
          if (car["Location Due Mne"] === station || car["Current Location Mne"] === station) {
            cars.push(data[i]);
          }
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_owner(owner) {
    let cars = [];

    // If owner is not defined, then set it to "None"
    if (owner === undefined) {
      owner = "None";
    }

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (owner.toUpperCase() === "ALL" || owner === "") {
        cars.push(data[i]);
      } else if (car["Fleet Owner Code"] === owner) {
        cars.push(data[i]);
      } else {
        continue;
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_tyres(tyre) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (check_owner(car, owner)) {
        if (car["Trunk Key"].substring(0, 1) === tyre || tyre === "All") {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_accessory(accessory) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      let found = false;
      
      if (check_owner(car, owner)) {
        for (let j = 1; j < 10; j++) {
          if ((car["Accessory 0" + j.toString()] === accessory || accessory === "All") && !found) {
            cars.push(data[i]);
            found = true;
          }
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_payment_method(Method) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Fleet Owner Code"] === owner) {
        if (Method === "All") {
          cars.push(data[i]);
        } else if (car["Creditclub Code"] === Method && (car["Current Status"] !== "ON HAND" && car["Current Status"] !== "UNAVAILABLE")) {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_RA(length) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Fleet Owner Code"] === owner) {
        if (length === "All") {
          cars.push(data[i]);
        } else if (length === "NaN") {
          if (car["Rental Agreement Num"].length !== 10 && car["Rental Agreement Num"].length !== 9) {
            cars.push(data[i]);
          }
        } else {
          if (car["Rental Agreement Num"].length === Number(length)) {
            cars.push(data[i]);
          }
        } 
      } 
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_out_of_town_cars() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      
      if (car["Fleet Owner Code"] === owner) {
        if (car["Location Due Mne"] !== "TOS" && 
            car["Location Due Mne"] !== "TO0" && 
            car["Location Due Mne"] !== "T1Y" && 
            car["Location Due Mne"] !== "T6O" && 
            car["Location Due Mne"] !== "TR7" && 
            car["Location Due Mne"] !== "TO7" && 
            car["Location Due Mne"] !== "E9Z" &&
            car["Location Due Mne"] !== "R4S") 
        {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function get_hold_cards() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Fleet Owner Code"] === owner) {
        if (car["STATUS3"].length > 0) {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function handleSearch() {
    let cars = [];
    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Fleet Owner Code"] === owner || owner === "All" || owner === "") {
        if (search.length === 1) {
          if (car["Car Group"].includes(search.toUpperCase())) {
            cars.push(data[i]);
          }
        } else if (search.includes(",")) {
          
          let search_array = search.split(",");

          {/* Sort the array from the longest to the shortest */}
          search_array.sort((a, b) => b.length - a.length);

          {/* If the first element is a body type, then check if the car group is in the array */}
          if (search_array[0].length > 1) {
            let bodyType = search_array[0].toUpperCase();
            
            if (bodyType === "VAN") {
              for (let j = 1; j < search_array.length; j++) {
                if (car["Body Type"].includes(bodyType) && car["Car Group"].includes(search_array[j].toUpperCase())) {
                  cars.push(data[i]);
                }
              }
            } else if (bodyType === "EL") {
              for (let j = 1; j < search_array.length; j++) {
                if (car["Fuel"] === "E" && car["Car Group"].includes(search_array[j].toUpperCase())) {
                  cars.push(data[i]);
                }
              }
            } else {
              for (let j = 1; j < search_array.length; j++) {
                if (car["Car Group"].includes(search_array[j].toUpperCase()) && car["Body Type"] !== "VAN") {
                  cars.push(data[i]);
                }
              }
            }
            
          } else {
            for (let j = 0; j < search_array.length; j++) {
              if (car["Car Group"].includes(search_array[j].toUpperCase())) {
                cars.push(data[i]);
              }
            }
          }
        } else if (car["Registration Number"].includes(search.toUpperCase()) ||
              car["MVA"].includes(search.toUpperCase()) ||
              car["Current Status"].includes(search.toUpperCase()) ||
              car["Rental Agreement Num"].includes(search.toUpperCase()) ||
              car["Body Type"].includes(search.toUpperCase()) ||
              (search.toLocaleUpperCase() === "EL" && car["Fuel"] === "E"))
        {
          cars.push(data[i]);
        }
      }
      
    sortCars(cars, "ASC", "Car Group");
    }
  }

  return (
    <>

      {/* Before giving file */}
      {data.length === 0 && 
        <div className='start'>
          <label htmlFor="file-input" className='file-label'>Choose a file</label>
          <p>File must be in .xlsx format</p>
          <p>File must contain only one sheet</p>
          <input 
            type="file" 
            id="file-input"
            onChange={() => fetch_data()}
            className='file-input'
          />
        </div>
      }

      {/* Header */}
      {data.length > 0 &&
        <div className="header">
          <div className="logo-container">
            <img src={logo} alt="Avis Logo" className="logo"/>
          </div>
          <div className="search-container">
            <form className="search-form"
              onSubmit={(e) => {
                e.preventDefault();
                handleSearch();
              }}
            >
              <input
                type="text"
                placeholder="Search"
                onChange={(e) => setSearch(e.target.value)}
                className="search-bar"
              />
            </form>
            <button type="submit" className="search-button" onClick={() => handleSearch()}>Search</button>
          </div>
        </div>
      }

      {/* Main Area */}
      {data.length > 0 &&
        <div className="main-container">
          <section className="top-area">
            <Selection title="Owner"              func={get_owner} owner={owner} setOwner={setOwner}/>
            <Selection title="Station"            func={get_all} owner={owner} setOwner={setOwner} stations={stations}/>
            <Selection title="Service"            func={get_serivce} owner={owner} setOwner={setOwner}/>
            <Selection title="Overdue RA/VTC"     func={get_overdue_RA} owner={owner} setOwner={setOwner}/>
            <Selection title="In Hold"            func={get_hold_cards} owner={owner} setOwner={setOwner}/>
            <Selection title="Buy Back"           func={get_buy_back} owner={owner} setOwner={setOwner}/>
            <Selection title="Tyres"              func={get_tyres} owner={owner} setOwner={setOwner}/>
            <Selection title="Accessory"          func={get_accessory} owner={owner} setOwner={setOwner}/>
            <Selection title="Credentials"        func={get_payment_method} owner={owner} setOwner={setOwner}/>
            <Selection title="RA/VTC"             func={get_RA} owner={owner} setOwner={setOwner}/>
            <Selection title="Out of Town"        func={get_out_of_town_cars} owner={owner} setOwner={setOwner}/>
          </section>

          <section className="bottom-area">
            <table className="table">
              <Table_Head cars={cars} sortCars={sortCars}/>
              <Table_Body cars={cars} fix_duplicate_status={fix_duplicate_status} />
              <Table_Summary cars={cars}/>
            </table>
          </section>
        </div>
      }
    </>
  )
}

function Table_Head({ cars, sortCars }) {

  const [sortDirection, setSortDirection] = useState("ASC");

  return (
    <thead className="table-head">
      <tr className="table-head-row">
        <th onClick={() => {sortCars(cars, sortDirection, "Body Type"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>BODY</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Make / Model"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>MODEL</th>
        <th onClick={() => {sortCars(cars, sortDirection, "MVA"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>MVA</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Registration Number"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>REG</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Current Status"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>STATUS</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Current Location Mne"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>CUR STA</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Location Due Mne"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>IN STA</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Checkin Datetime"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>CHECKIN</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Car Group"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>GROUP</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Vehicle Mileage"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>KM</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Ignition Key"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>IGNIT KEY</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Rental Agreement Num"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>MOVEMENT</th>
        <th onClick={() => {sortCars(cars, sortDirection, "Trunk Key"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>TRUNK KEY</th>
        <th onClick={() => {sortCars(cars, sortDirection, "STATUS3"); setSortDirection(sortDirection === "ASC" ? "DESC" : "ASC")}}>STATUS</th>
      </tr>
    </thead>
  )
}

function Table_Body({ cars, fix_duplicate_status }) {

  function displayLoc(car) {

    if (car["Rental Agreement Num"].length === 0) {
      return "";
    } else {
      return car["Location Due Mne"];
    }
  }

  function format_time(time) {

    if (time === undefined) {
      return "";
    }

    let newTime = time.toUTCString().substring(5, 22);
    let month = newTime.substring(3, 6);
  
    if (month === "Jan") {
      month = "01";
    } else if (month === "Feb") {
      month = "02";
    }  else if (month === "Mar") {
      month = "03";
    } else if (month === "Apr") {
      month = "04";
    } else if (month === "May") {
      month = "05";
    } else if (month === "Jun") {
      month = "06";
    } else if (month === "Jul") {
      month = "07";
    } else if (month === "Aug") {
      month = "08";
    } else if (month === "Sep") {
      month = "09";
    } else if (month === "Oct") {
      month = "10";
    } else if (month === "Nov") {
      month = "11";
    } else if (month === "Dec") {
      month = "12";
    }
    
    let day = newTime.substring(0, 2);
    let year = newTime.substring(7, 11);

    return `${day}/${month}/${year}`;

  }
  
  const Colors = {
    "ON HAND": "rgb(220, 220, 220)",
    "ON RENT": "rgb(0, 200, 0)",
    "ON MOVE": "rgb(0, 150, 0)",
    "ON RENT,OVDU": "rgb(200, 0, 0)",
    "UNAVAILABLE": "rgb(180, 100, 0)",
    "OVERDUE": "rgb(250, 250, 0)",
    "": "white"
  }
  
  function format_milage(milage) {
    if (milage === undefined) {
      return "";
    }

    const formated_milage = Number(dateToExcelSerialNumber(milage));
    return formated_milage;
  }

  return (
    <tbody className="table-body">
      {cars.map((car, index) => (
        <tr
          className="table-body-row"
          key={index}
          style={{"--color": Colors[car["Current Status"]]}}
        >
          <td>{car["Body Type"]}</td>
          <td>{car["Make / Model"]}</td>
          <td>{car["MVA"]}</td>
          <td>{car["Registration Number"]}</td>
          <td style={{ backgroundColor: Colors[car["Current Status"]]}}>
            {car["Current Status"]}
          </td>
          <td>{car["Current Location Mne"]}</td>
          <td>{displayLoc(car)}</td>
          <td>{format_time(car["Checkin Datetime"])}</td>
          <td>{car["Car Group"]}</td>
          <td>{car["Vehicle Mileage"]}</td>
          <td>{car["Ignition Key"]}</td>
          <td
          style={{
            backgroundColor: car["Rental Agreement Num"].length === 10 && 
            car["Checkout Location"].slice(-1) === "A" ? "rgb(255, 20, 20)" : 
            car["Rental Agreement Num"].length === 10 && car["Checkout Location"].slice(-1) === "B" ? "rgb(50, 50, 250)" : 
            car["Rental Agreement Num"].length === 9 ? "rgb(150, 150, 150)" : "",
            paddingLeft: "1.6rem"
          }}
          >{car["Rental Agreement Num"].substring(1)}</td>
          <td>{car["Trunk Key"]}</td>
          <td>{fix_duplicate_status(car["STATUS3"])}</td>
        </tr>
      ))}
    </tbody>
  )
}

function Table_Summary({ cars }) {
  
  const [showCarTypes, setShowCarTypes] = useState(false);

  function get_dict_of_car_types(cars) {

    let car_numbers = {
      "Person": {},
      "Vans": {},
      "Car_Types": {}
    };

    for (let i = 0; i < cars.length; i++) {

      let carGroup = cars[i]["Car Group"];

      if (car_numbers["Car_Types"][carGroup] === undefined) {
        car_numbers["Car_Types"][carGroup] = carGroup;
      }

      let carType = cars[i]["Body Type"];
      
      if (carType === "VAN") {
        if (car_numbers["Vans"][carGroup] === undefined) {
          car_numbers["Vans"][carGroup] = 1;
        } else {
          car_numbers["Vans"][carGroup] += 1;
        }
      } else {
        if (car_numbers["Person"][carGroup] === undefined) {
          car_numbers["Person"][carGroup] = 1;
        } else {
          car_numbers["Person"][carGroup] += 1;
        }
      }
    }
    return car_numbers;
  }

  function get_num_of_RA(cars) {
    let num_of_RA = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Rental Agreement Num"].length === 10) {
        num_of_RA += 1;
      }
    }
    return num_of_RA;
  }

  function get_num_of_VTC(cars) {
    let num_of_VTC = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Rental Agreement Num"].length === 9) {
        num_of_VTC += 1;
      }
    }
    return num_of_VTC;
  }

  function get_num_of_avis_rentals(cars) {
    let num_of_avis_rentals = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Checkout Location"].slice(-1) === "A") {
        num_of_avis_rentals += 1;
      }
    }
    return num_of_avis_rentals;
  }

  function get_num_of_budget_rentals(cars) {
    let num_of_budget_rentals = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Checkout Location"].slice(-1) === "B") {
        num_of_budget_rentals += 1;
      }
    }
    return num_of_budget_rentals;
  }

  function get_num_of_summer_tyres(cars) {
    let num_of_summer_tyres = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Trunk Key"].substring(0, 1) === "S") {
        num_of_summer_tyres += 1;
      }
    }
    return num_of_summer_tyres;
  }

  function get_num_of_winter_tyres(cars) {
    let num_of_winter_tyres = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Trunk Key"].substring(0, 1) === "P") {
        num_of_winter_tyres += 1;
      }
    }
    return num_of_winter_tyres;
  }

  function get_num_of_spike_free_tyres(cars) {
    let num_of_spike_free_tyres = 0;

    for (let i = 0; i < cars.length; i++) {
      if (cars[i]["Trunk Key"].substring(0, 1) === "V") {
        num_of_spike_free_tyres += 1;
      }
    }
    return num_of_spike_free_tyres;
  }

  let car_types = get_dict_of_car_types(cars);

  return (
    <tfoot className="table-summary">
      <tr className="table-summary-row">
        <td
          onClick={() => {setShowCarTypes(!showCarTypes)}}
          onMouseLeave={() => setShowCarTypes(false)}
        >Cars: {cars.length}
        
        {showCarTypes &&
        <div className='cartypes-section'>
          <div className='cartypes'>
            <p>Car Types</p>
            {Object.entries(car_types["Car_Types"]).map((car, index) => (
              <p key={index}>{car[0]}</p>
            ))}
          </div>

          <div className='cartypes'>
            <p>Person</p>
            {Object.entries(car_types["Car_Types"]).map((type, _) => (
              car_types["Person"][type[0]] !== undefined 
                ? 
              <p key={type[0]}>{car_types["Person"][type[0]]}</p> 
                : 
              <p style={{height: "100%"}}></p>
            ))}
          </div>

          <div className='cartypes'>
            <p>Vans</p>
            {Object.entries(car_types["Car_Types"]).map((type, _) => (
              car_types["Vans"][type[0]] !== undefined 
                ? 
              <p key={type[0]}>{car_types["Vans"][type[0]]}</p> 
                : 
              <p style={{height: "100%"}}></p>
            ))}
          </div> 
        </div>}
        
        </td>
        <td>RA: {get_num_of_RA(cars)}</td>
        <td>VTC: {get_num_of_VTC(cars)}</td>
        <td>Avis Cars: {get_num_of_avis_rentals(cars)}</td>
        <td>Budget Cars: {get_num_of_budget_rentals(cars)}</td>
        <td>Summer Tyres: {get_num_of_summer_tyres(cars)}</td>
        <td>Winter Tyres: {get_num_of_winter_tyres(cars)}</td>
        <td>Spike free Tyres: {get_num_of_spike_free_tyres(cars)}</td>
      </tr>
    </tfoot>
  )
}

function Selection({ title, func, owner, setOwner, stations }) {

  if (title === "Credentials") {

    const [param, setParam] = useState("All");

    return (
      <div className="selection">
        <p>{title}</p>
        <select onChange={(e) => setParam(e.target.value)}>
          <option value="All">-</option>
          <option value="CX">CX</option>
          <option value="CM">CM</option>
          <option value="CA">CA</option>
          <option value="AV">AV</option>
          <option value="S/">S/</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "Accessory") {
      
    const [param, setParam] = useState("All");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='accessory-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="All">-</option>
          <option value="NV">GPS</option>
          <option value="DL">HENGEFESTE</option>
          <option value="CR">CRUISE CONTROL</option>
          <option value="IQ">USB INNGANG</option>
          <option value="PH">BLUETOOTH</option>
          <option value="SR">SKISTATIV</option>
          <option value="XM">4X4</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "Tyres") {
    
    const [param, setParam] = useState("All");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='tyre-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="All">-</option>
          <option value="P">VINTER</option>
          <option value="V">PIGGFRITT</option>
          <option value="S">SOMMER</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "RA/VTC") {

    const [param, setParam] = useState("All");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='RA-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="All">-</option>
          <option value="10">RA</option>
          <option value="9">VTC</option>
          <option value="NaN">NONE</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "Station") {

    const [param, setParam] = useState("All");
    
    return (
      <div className="selection">
        <p>{title}</p>
        <select className='station-selection' onChange={(e) => setParam(e.target.value)} defaultValue={param}>
          <option value="All">All</option>
          {stations.map((station, index) => (
            <option key={index} value={station}>{station}</option>
          ))}
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "Owner") {

    return (
      <div className="selection">
        <p>{title}</p>
        
        <form className="owner-form"
          onSubmit={(e) => {
            e.preventDefault();
            setOwner(e.target.value);
          }}
        >
          <input
            type="text"
            placeholder="Owner"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            className="owner-bar"
          />
        </form>
        <SearchButton func={func} param={owner} />
      </div>
    )
  }

  return (
    <div className="selection"
    >
      <p>{title}</p>
      <SearchButton func={func} />
    </div>
  )
}

function SearchButton({func, param}) {

  if (param) {
    return (
      <button
        onClick={() => func(param)}
      >
        Search
      </button>
    )
  } else {
    return (
      <button
        onClick={() => func()}  
      >
        Search
      </button>
    )
  }
}