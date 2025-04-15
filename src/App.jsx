import './App.css'
import * as XLSX from 'xlsx/xlsx.mjs';
import { useState, useEffect } from 'react';
import AvisFleets from '../data/AvisFleets.json';
import BudgetFleets from '../data/BudgetFleets.json';
import Stations from '../data/Stations.json';
import Avislogo from "../public/Avis.png"

import B_WF_P from "../public/B_Wireframe_PersonT.png"
import C_WF_P from "../public/C_Wireframe_PersonT.png"
import D_WF_P from "../public/D_Wireframe_PersonT.png"
import E_WF_P from "../public/E_Wireframe_PersonT.png"
import H_WF_P from "../public/H_Wireframe_PersonT.png"
import N_WF_P from "../public/N_Wireframe_PersonT.png"
import C_WF_V from "../public/C_Wireframe_VanT.png"
import E_WF_V from "../public/E_Wireframe_VanT.png"
import F_WF_V from "../public/F_Wireframe_VanT.png"

import { motion, AnimatePresence } from "framer-motion"

export default function App() {
  
  const [typeFetch, setTypeFetch] = useState(0);
  const [data, setData] = useState([]);
  const [cars, setCars] = useState([]);
  const [search, setSearch] = useState("");
  const [owner, setOwner] = useState("64442");
  const [stations, setStations] = useState([]);
  const [previewStation, setPreviewStation] = useState(null);
  const [previewCar, setPreviewCar] = useState(null);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

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

    if (sortingType === "Vehicle Mileage") {
      if (sortDirection === "ASC") {
        sortedCars.sort((a, b) => {
        if (Number(a[sortingType]) < Number(b[sortingType])) {
            return -1;
          }
          if (Number(a[sortingType]) > Number(b[sortingType])) {
            return 1;
          }
          if (Number(a[sortingType]) === Number(b[sortingType])) {
            return 0;
          }
        });
      } else if (sortDirection === "DESC") {
        sortedCars.sort((a, b) => {
          if (Number(a[sortingType]) > Number(b[sortingType])) {
            return -1;
          }
          if (Number(a[sortingType]) < Number(b[sortingType])) {
            return 1;
          }
          if (Number(a[sortingType]) === Number(b[sortingType])) {
            return 0;
          }
        });
      }
    }

    else {
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
    }
    setCars(sortedCars);
  }

  async function fetch_data(fetching=false) {
    const baseDate = new Date(1900, 0, 1);
    const input = document.getElementById('file-input'); // Assuming your input element has id="file-input"

    let file = null;

    if (!fetching) {
      if (!input.files || input.files.length === 0) {
        console.error('No file selected');
        return;
      }
      file = input.files[0]; // Get the first selected file
    } else {
      file = await fetch("../AvisFleetTool/public/data.xlsx").then((response) => {return response.blob();});
    }

    const reader = new FileReader();

    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { cellDates: true });

      const sheet_name_list = workbook.SheetNames;
      const xlData = XLSX.utils.sheet_to_json(workbook.Sheets[sheet_name_list[0]]);

      xlData.pop(); // Remove the last row in the sheet

      // Remove the car with the registration number "DL80552"
      let xlData_filtered = xlData.filter((car) => (car["Registration Number"] !== "DL80552" && car["Registration Number"] !== "ZH22397"));

      setData(xlData_filtered);

      let cars = [];
      for (let i = 0; i < xlData_filtered.length; i++) {

        // Check if the json has the "Checkin Datetime" key
        if (xlData_filtered[i]["Checkin Datetime"] !== undefined && xlData_filtered[i].hasOwnProperty("Checkin Datetime") && typeof xlData_filtered[i]["Checkin Datetime"] === "number") {          
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Checkin Datetime"] - 1);
          xlData_filtered[i]["Checkin Datetime"] = newDate;
        }

        // Check if the json has the "Checkin Datetime" key
        if (xlData_filtered[i]["Checkout Datetime"] !== undefined && xlData_filtered[i].hasOwnProperty("Checkout Datetime") && typeof xlData_filtered[i]["Checkout Datetime"] === "number") {          
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Checkout Datetime"]);
          xlData_filtered[i]["Checkout Datetime"] = newDate;
        }

        // Fix conversion of "Vehicle Mileage" to number
        if (typeof xlData_filtered[i]["Vehicle Mileage"] !== "number") {
          xlData_filtered[i]["Vehicle Mileage"] = String(dateToExcelSerialNumber(xlData_filtered[i]["Vehicle Mileage"]));
        }

        // Fix conversion of "Registration Date", "Inspection Date", "Disposal Date", "Last Movement" and "Delivery Date" to "Date
        if (typeof xlData_filtered[i]["Registration Date"] === "number") {
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Registration Date"]);
          xlData_filtered[i]["Registration Date"] = newDate;
        }

        if (typeof xlData_filtered[i]["Inspection Date"] === "number") {
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Inspection Date"]);
          xlData_filtered[i]["Inspection Date"] = newDate;
        }

        if (typeof xlData_filtered[i]["Disposal Date"] === "number") {
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Disposal Date"]);
          xlData_filtered[i]["Disposal Date"] = newDate;
        }

        if (typeof xlData_filtered[i]["Last Movement"] === "number") {
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Last Movement"]);
          xlData_filtered[i]["Last Movement"] = newDate;
        }

        if (typeof xlData_filtered[i]["Delivery Date"] === "number") {
          let newDate = new Date(baseDate);
          newDate.setDate(baseDate.getDate() + xlData_filtered[i]["Delivery Date"]);
          xlData_filtered[i]["Delivery Date"] = newDate;
        }

        cars.push(xlData_filtered[i]);
      }
      
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

    const Service_offset = 1500;

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Make / Model"] == "BMWI X3EL") {
        continue;
      }

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

      let curDate = new Date().getDate();
      let curMonth = new Date().getMonth();
      let curYear = new Date().getFullYear();

      if (car["Checkin Datetime"] === undefined || car["Checkin Datetime"] === "" || car["Checkin Datetime"] === null) {
        continue;
      }
      
      let checkinDate = car["Checkin Datetime"].getDate();
      let checkinMonth = car["Checkin Datetime"].getMonth();
      let checkinYear = car["Checkin Datetime"].getFullYear();
      
      if (car["Fleet Owner Code"] === owner) {
        if (car["Current Status"] === "ON RENT,OVDU" || car["Current Status"] === "OVERDUE" || car["Current Status"] === "ON MOVE,OVDU") {
          cars.push(data[i]);
        }
        else if (car["Rental Agreement Num"].length === 10 || car["Rental Agreement Num"].length === 9) {
          if (curYear > checkinYear || (curYear === checkinYear && curMonth > checkinMonth) || (curYear === checkinYear && curMonth === checkinMonth && curDate > checkinDate)) {
            cars.push(data[i]);
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
        if (car["STATUS3"].indexOf("BB") !== -1 || ((car["Ignition Key"].substring(3, 8) >= Number(car["Ignition Key"].substring(0, 2))*1000) && ((Number(car["Vehicle Mileage"]) + BB_number_offset) >= (Number(car["Ignition Key"].substring(0, 2))*1000).toString()))) {
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
        for (let j = 1; j <= 10; j++) {
          const accessoryKey = `Accessory ${j.toString().padStart(2, '0')}`;
          if ((car[accessoryKey] === accessory || accessory === "All") && !found) {
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

    const forsikringsleie = ["VK", "FS", "CZ", "2J", "S2", "86", "VR", "VC", "UK", "J5", "S3", "6Y", "ER", "RH", "CL", "9S", "FH", "O1", "TA", "T3"]

    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Fleet Owner Code"] === owner) {
        if (length === "All") {
          cars.push(data[i]);

        // Check if it is not a RA or VTC
        } else if (length === "NaN") {
          if (car["Rental Agreement Num"].length !== 10 && car["Rental Agreement Num"].length !== 9) {
            cars.push(data[i]);
          }

        // Check if it is a Forsikringsleie
        } else if (length === "Forsikringsleie") {
          
          if (car["Rental Agreement Num"].length === 10 && (forsikringsleie.includes(car["Checkout Rate Code"]))) 
          {
            cars.push(data[i]);
          }
        } else {

          // Check if it is a AVIS rental
          if (length === "10A") {
            if (car["Rental Agreement Num"].length === Number(10) && car["Checkout Location"].slice(-1) === "A") {
              cars.push(data[i]);
            }

          // Check if it is a Budget rental
          } else if (length === "10B") {
            if (car["Rental Agreement Num"].length === Number(10) && car["Checkout Location"].slice(-1) === "B") {
              cars.push(data[i]);
            }
          
          // Check if it is a VTC
          } else if (length === "9") {
            if (car["Rental Agreement Num"].length === Number(9)) {
              cars.push(data[i]);
            }
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
            car["Location Due Mne"] !== "R4S" &&
            car["Location Due Mne"] !== "") 
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

  function match_car_group_search(car, search) {
    return car["Car Group"].includes(search.toUpperCase());
  }

  function handleSearch() {
    let cars = [];
    let temp_cars = data.slice();
    let final_cars = [];

    let accessory = {
      "GPS": "NV",
      "HENGERFESTE": "DL",
      "SKISTATIV": "SR"
    }

    if (search.length === 0 || search === "") {
      return sortCars(data, "ASC", "Car Group");
    }

    {/* If the search is only one letter, then check if the car group includes the letter */}
    if (search.length === 1) {
      for (let i = 0; i < data.length; i++) {
        let car = data[i];
        if (car["Car Group"].includes(search.toUpperCase())) {
          cars.push(data[i]);
        }
      }
    }

    let search_array = [search];

    if (search.includes(",")) {

      search_array = search.split(",");
    
      {/* Sort the array from the longest to the shortest and converts every element in the search array to uppercase */}
      search_array.sort((a, b) => b.length - a.length);
    }
    
    search_array = search_array.map((element) => element.toUpperCase());

    for (let i = 0; i < search_array.length; i++) {
      let selector = search_array[i];

      if (selector.length === 3) {
        for (let j = 0; j < temp_cars.length; j++) {
          let car = temp_cars[j];

          if (car["Location Due Mne"] === selector || car["Current Location Mne"] === selector) {
            final_cars.push(car);
          }
        }
        cars = final_cars;
      }

      else if (selector.length > 1) {
        for (let j = temp_cars.length - 1; j >= 0; j--) {
          let car = temp_cars[j];
          let deleting = true;

          if (selector === "PERSON") {
            if (car["Body Type"] != "VAN") {
              deleting = false;
            }
          }

          if (selector === "VANS") {
            if (car["Body Type"] === "VAN") {
              deleting = false;
            }
          }

          if (selector === "YARIS" && car["Make / Model"] === "TYAR ISGH") { deleting = false; }

          if (selector === "SCROSS" && car["Make / Model"] === "SSCR OS4H") { deleting = false; }

          if (selector === "RAV4" && car["Make / Model"] === "TR4G 4PIH") { deleting = false; }

          if (selector === "ACROSS" && car["Make / Model"] === "SACR 4PIH") { deleting = false; }

          if (selector === "OCTAVIA" && car["Make / Model"] === "OCTR SWDA") { deleting = false; }

          if (selector === "COROLLA" && car["Make / Model"] === "TCTS GAH") { deleting = false; }

          if ((selector === "MAZDA" || selector === "CX60") && car["Make / Model"] === "MCX6 04GH") { deleting = false; }

          if ((selector === "LEXUS" || selector === "NX450") && car["Make / Model"] === "LNX4 50H4") { deleting = false; }

          // if (selector === "ID4" && car["Make / Model"] === "VWID 4GTX") { deleting = false; }

          // if (selector === "ID3" && car["Make / Model"] === "VWID 3ELA") { deleting = false; }

          // if (selector === "EC4" && car["Make / Model"] === "CITR EC4E") { deleting = false; }

          for (const [key, value] of Object.entries(car)) {
            if (typeof value === 'string' && value.includes(selector)) {
              deleting = false;
            } else {
              if (key === "Accessory 01" || key === "Accessory 02" || key === "Accessory 03" || key === "Accessory 04" || key === "Accessory 05" || key === "Accessory 06" || key === "Accessory 07" || key === "Accessory 08" || key === "Accessory 09") {
                if (value === accessory[selector] && value !== "") {
                  deleting = false;
                }
              }
            }
          }
          
          if (deleting) {temp_cars.splice(j, 1);}
        }
        cars = temp_cars;
      }

      else {
        for (let j = 0; j < temp_cars.length; j++) {
          let car = temp_cars[j];
          if (match_car_group_search(car, selector)) {
            final_cars.push(car);
          }
        }
        cars = final_cars;
      }
    }
    sortCars(cars, "ASC", "Car Group");
  }

  function check_credentials(username, password) {
    if (username === "QWEASD" && password === "potet") {
      setLoggedIn(true);
      return true;
    } else {
      return false;
    }
  }

  function credidentials() {
    if (!check_credentials(username, password)) {
      alert("Wrong credentials")
    } 
  }

  return (
    <>
      {/* Before giving file */}
      {!loggedIn &&
        <div className='log-in-container'>
          <div className='log-in'>
            <h1 className='log-in-title'>Log in</h1>
              <div className='log-in-inputs'>
                <input 
                type="text" 
                placeholder="Username" 
                className='log-in-input' 
                onChange={(e) => setUsername(e.target.value)} 
                onKeyDown={(e) => { if (e.key === 'Enter') credidentials(); }}
                />
                <input 
                type="password" 
                placeholder="Password" 
                className='log-in-input' 
                onChange={(e) => setPassword(e.target.value)} 
                onKeyDown={(e) => { if (e.key === 'Enter') credidentials(); }}
                />
              </div>
            <button className='log-in-button' onClick={() => {credidentials();}}>Log in</button>
          </div>
        </div>}
      {loggedIn && data.length == 0 &&
        <div className='start'>
          <label htmlFor="file-input" className='file-label'>Choose a file</label>
          <p>File must be in .xlsx format</p>
          <p>File must contain only one sheet</p>
          <input
            type="file" 
            id="file-input"
            onChange={() => fetch_data(false)}
            className='file-input'
            accept='.xlsx'
          />
        </div>}

      {/* Header */}
      {data.length > 0 &&
        <div className="header">
          <div className="logo-container">
            <img src={Avislogo} alt="Avis Logo" className="logo"/>
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
            {/* {typeFetch === 0 && <Selection title="Owner"              func={get_owner} owner={owner} setOwner={setOwner}/>} */}
            <Selection title="Station"            func={get_all} owner={owner} setOwner={setOwner} stations={stations}/>
            <Selection title="Service"            func={get_serivce} owner={owner} setOwner={setOwner}/>
            <Selection title="Overdue RA/VTC"     func={get_overdue_RA} owner={owner} setOwner={setOwner}/>
            <Selection title="In Hold"            func={get_hold_cards} owner={owner} setOwner={setOwner}/>
            <Selection title="Buy Back"           func={get_buy_back} owner={owner} setOwner={setOwner}/>
            <Selection title="Tyres"              func={get_tyres} owner={owner} setOwner={setOwner}/>
            <Selection title="Accessory"          func={get_accessory} owner={owner} setOwner={setOwner}/>
            {typeFetch === 0 && <Selection title="Credentials"        func={get_payment_method} owner={owner} setOwner={setOwner}/>}
            {typeFetch === 0 && <Selection title="RA/VTC"             func={get_RA} owner={owner} setOwner={setOwner}/>}
            <Selection title="Out of Town"        func={get_out_of_town_cars} owner={owner} setOwner={setOwner}/>
          </section>

          <section className="bottom-area">
            <table className="table">
              <Table_Head cars={cars} sortCars={sortCars}/>
              <Table_Body cars={cars} fix_duplicate_status={fix_duplicate_status} setPreviewStation={setPreviewStation} setPreviewCar={setPreviewCar}/>
            </table>
          </section>
          <Table_Summary cars={cars}/>
          <Preview_Station previewStation={previewStation} setPreviewStation={setPreviewStation}/>
          <Preview_car previewCar={previewCar} setPreviewCar={setPreviewCar}/>
        </div>
      }
    </>
  )
}

function Preview_Station({ previewStation, setPreviewStation }) {

  function show_owner_details(station, racf) {
    const Fleet_code = station["Fleet Code"];
    const Fleet_name = station["Fleet Name"];
    const Supervisor = station["Supervisor"];
    const address1 = station["Address 1"];
    const address2 = station["Address 2"];
    const zipcode = station["Zipcode"];
    const city = station["City"];
    const phone = station["Telephone"].substring(0, 3) + " " + station["Telephone"].substring(4, 7) + " " + station["Telephone"].substring(7, 9) + " " + station["Telephone"].substring(9, 12);

    const station_codes = station["CODES"];
    const codes_code = Object.keys(station_codes).filter(key => key.includes("CODE"));
    const codes_num = Object.keys(station_codes).filter(key => key.includes("NUM"));

    const codes = {
      "AVIS_CODE": "Avis",
      "AVIS_NUM": "Avis",
      "Avis Vans_CODE": "Avis Vans",
      "Avis Vans_NUM": "Avis Vans",
      "Budget_CODE": "Budget",
      "Budget_NUM": "Budget",
      "Select_CODE": "Select",
      "Select_NUM": "Select",
      "Prestige_CODE": "Prestige",
      "Prestige_NUM": "Prestige",
      "Eco/GG Month_CODE": "Eco Monthly",
      "Eco/GG Month_NUM": "Eco Monthly",
      "Eco/LEASING_CODE": "Eco Leasing",
      "Eco/LEASING_NUM": "Eco Leasing",
      "Month_CODE": "Monthly",
      "Month_NUM": "Monthly",
      "Month Van_CODE": "Month Vans",
      "Month Van_NUM": "Month Vans",
      "Leasing 12 months +_CODE": "Leasing 12 months +",
      "Leasing 12 months +_NUM": "Leasing 12 months +",
      "Leasing Vans 12 months +": "Leasing Vans 12 months +",
      "Leasing Vans 12 months +_1": "Leasing Vans 12 months +"
    }

    const text_space = "220px 1fr"

    return <div className='preview-station'>

      {/* Fleet Code and Fleet Name */}
      <div>
        {racf === "A" ? 
          <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Fleet Code Avis: </b>{Fleet_code}</p>
          :
          <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Fleet Code Budget: </b>{Fleet_code}</p>
        }
        <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Fleet Name:</b> {Fleet_name}</p>
        <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Place:</b> {city}</p>
      </div>

      {/* Supervisor and Phonenumber */}
      <div>
        <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Supervisor:</b> {Supervisor}</p>
        <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Telephone:</b> {phone}</p>
      </div>

      {/* Codes */}
      <div>
        {codes_code.map((key, index) => (
          <div key={index} style={{display: "grid", gridTemplateColumns: text_space}}>
            <b>{codes[key]}:</b> 
            <div style={{display: "grid", gridTemplateColumns: "50px 1fr"}}>
              <span>
                {station_codes[key]}
              </span>
              <span>
                - {station_codes[codes_num[index]]}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Address */}
      <div style={{display: "grid", gridTemplateColumns: text_space}}>
        <div className='preview-address'>
          <b>Address 1:</b>
          <b>Address 2:</b>
          <b>Zip Code:</b>
          <b>City:</b>
        </div>
        <div className='preview-address'>
          <p>{address1}</p>
          <p>{address2}</p>
          <p>{zipcode}</p>
          <p>{city}</p>
        </div>
      </div>
    </div>;
  }

  function search_for_owner(station, racf) {
    const fleets = Object.keys(racf === "A" ? AvisFleets : BudgetFleets);
    for (let i = 0; i < fleets.length; i++) {
      const fleet = racf === "A" ? AvisFleets[fleets[i]] : BudgetFleets[fleets[i]];
      const district = Object.keys(fleet);
      for (let j = 0; j < district.length; j++) {
        const stations = fleet[district[j]];
        if (stations.includes(station)) {
          const fleet_number = fleets[i].split("-")[1].substring(1, 6)
          for (let k = 0; k < Stations.length; k++) {
            const found_fleet = Stations[k]["Fleet Code"];
            if (found_fleet === fleet_number) {
              const station_codes = Stations[k]["CODES"];
              const codes_keys = Object.keys(station_codes);
              for (let l = 0; l < codes_keys.length; l++) {
                if (station_codes[codes_keys[l]] === station) {
                  return show_owner_details(Stations[k], racf);
                }
              }
            }
          }
        }
      }
    }
    return "Utenlands / Hvis ikke den er utenlands, mail Kevin om å legge til stasjonen";
  }

  return (
    <>
      <AnimatePresence>
        {previewStation !== null &&
          <motion.div className="preview-station-container"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.3 }}
            key={previewStation[0] + previewStation[1]}
          >
            {search_for_owner(previewStation[0], previewStation[1])}
            <button className='preview-station-close-button'
              onClick={() => setPreviewStation(null)}
            >
              Close
            </button>
          </motion.div>
        }
      </AnimatePresence>
    </>
  )
}

function Preview_car({ previewCar, setPreviewCar }) {

  const Wireframe = {
    "A": B_WF_P,
    "B": B_WF_P,
    "C": C_WF_P,
    "D": D_WF_P,
    "E": E_WF_P,
    "F": E_WF_P,
    "H": H_WF_P,
    "I": B_WF_P,
    "J": D_WF_P,
    "K": D_WF_P,
    "L": E_WF_P,
    "M": E_WF_P,
    "N": N_WF_P,
    "O": E_WF_P,
    "P": E_WF_P,
    "X": E_WF_P,
    "B_V": C_WF_V,
    "C_V": C_WF_V,
    "D_V": E_WF_V,
    "E_V": E_WF_V,
    "F_V": F_WF_V,
    "G_V": F_WF_V,
    "H_V": F_WF_V,
    "I_V": E_WF_V,
    "J_V": E_WF_V,
    "L_V": E_WF_P,
    "M_V": E_WF_P,
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

  function show_car_details(car) {
    const text_space = "220px 1fr";
    return (
      <div className='preview-car'>
        <div className='preview-car-section'>
          <section className='details car-details'>
            <div>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>MVA:</b> {car["MVA"]}</p>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Reg Number:</b> {car["Registration Number"]}</p>
            </div>
            <div>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Car Group:</b> {car["Car Group"]}</p>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Body Type:</b> {car["Body Type"]}</p>
            </div>
            <div>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Make / Model:</b> {car["Make / Model"]}</p>
            </div>
          </section>
          <section className='details show-wireframe'>
            {car["Body Type"].toUpperCase() === "VAN" ?
              <img src={Wireframe[car["Car Group"] + "_V"]} alt="Car" className="car-image-van"/> 
              :
              <img src={Wireframe[car["Car Group"]]} alt="Car" className="car-image"/>  
            }
          </section>
          <section className='details rent-details'>
            <div>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Current Status:</b> {car["Current Status"]}</p>

              {car["Current Status"] === "ON HAND" &&
                <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Current Location:</b> {car["Current Location Mne"]}</p>
              }
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Location Due:</b> {car["Location Due Mne"]}</p>
            </div>
            <div>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Checkin:</b> {format_time(car["Checkin Datetime"])}</p>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Checkout:</b> {format_time(car["Checkout Datetime"])}</p>
              <p style={{display: "grid", gridTemplateColumns: text_space}}><b>Owner:</b> {car["Fleet Owner Code"]}</p>
            </div>
          </section>
        </div>
      </div>
    ) 
  }

  return (
    <>
      <AnimatePresence>
        {previewCar !== null &&
          <motion.div className="preview-car-container"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.3 }}
            key={previewCar}
          >
            {show_car_details(previewCar)}
            <button className='preview-car-close-button'
              onClick={() => setPreviewCar(null)}
            >
              Close
            </button>
          </motion.div>
        }
      </AnimatePresence>
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

function Table_Body({ cars, fix_duplicate_status, setPreviewStation, setPreviewCar }) {

  function displayLoc(car) {
    if (car["Rental Agreement Num"].length === 0) {
      return "";
    } else {
      return car["Location Due Mne"];
    }
  }

  function format_time(time) {

    if (time === undefined || time === "") {
      return "";
    }

    if (time.length === 7) {
      let month = time[2] + time[3] + time[4]
      if (month === "JAN") {
        month = "01";
      } else if (month === "FEB") {
        month = "02";
      } else if (month === "MAR") {
        month = "03";
      } else if (month === "APR") {
        month = "04";
      } else if (month === "MAY") {
        month = "05";
      } else if (month === "JUN") {
        month = "06";
      } else if (month === "JUL") {
        month = "07";
      } else if (month === "AUG") {
        month = "08";
      } else if (month === "SEP") {
        month = "09";
      } else if (month === "OCT") {
        month = "10";
      } else if (month === "NOV") {
        month = "11";
      } else if (month === "DEC") {
        month = "12";
      }
      return time[0] + time[1] + "/" + month + "/" + time[5] + time[6];
    }

    let newTime = time.toUTCString().substring(5, 22);
    let month = newTime.substring(3, 6);
  
    if (month === "Jan") {
      month = "01";
    } else if (month === "Feb") {
      month = "02";
    } else if (month === "Mar") {
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

  return (
    <tbody className="table-body">
      {cars.map((car, index) => (
        <tr
          className="table-body-row"
          key={index}
        >
          <td>{car["Body Type"]}</td>
          <td>{car["Make / Model"]}</td>
          <td>{car["MVA"]}</td>
          <td onClick={() => {setPreviewCar(car)}}>{car["Registration Number"]}</td>
          <td style={{ backgroundColor: Colors[car["Current Status"]]}}>{car["Current Status"]}</td>
          <td onClick={() => setPreviewStation([car["Current Location Mne"] , car["Current Location"].slice(-1)]) }>{car["Current Location Mne"]}</td>
          <td onClick={() => setPreviewStation([car["Location Due Mne"]     , car["Checkout Location"].slice(-1)])}>{displayLoc(car)}</td>
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
    <div className="table-summary">
      <div className="table-summary-row">
        <span
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
            {Object.entries(car_types["Car_Types"]).map((type, index) => (
              car_types["Person"][type[0]] !== undefined 
                ? 
              <p key={index}>{car_types["Person"][type[0]]}</p> 
                : 
              <p key={index} style={{height: "100%"}}></p>
            ))}
          </div>

          <div className='cartypes'>
            <p>Vans</p>
            {Object.entries(car_types["Car_Types"]).map((type, index) => (
              car_types["Vans"][type[0]] !== undefined 
                ? 
              <p key={index}>{car_types["Vans"][type[0]]}</p> 
                : 
              <p key={index} style={{height: "100%"}}></p>
            ))}
          </div> 
        </div>}
        
        </span>
        <span>RA: {get_num_of_RA(cars)}</span>
        <span>VTC: {get_num_of_VTC(cars)}</span>
        <span>Summer Tyres: {get_num_of_summer_tyres(cars)}</span>
        <span>Winter Tyres: {get_num_of_winter_tyres(cars)}</span>
        <span>Spike free Tyres: {get_num_of_spike_free_tyres(cars)}</span>
      </div>
    </div>
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
          <option value="DL">HENGERFESTE</option>
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
          <option value="10A">RA AVIS</option>
          <option value="10B">RA Budget</option>
          <option value="Forsikringsleie">Forsikringsleie</option>
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
            onBlur={(e) => setOwner(e.target.value)}
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