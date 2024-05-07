import './App.css'
import * as XLSX from 'xlsx/xlsx.mjs';
import { useState } from 'react';
import logo from "../public/Avis.png"

export default function App() {
  
  const [data, setData] = useState([]);
  const [cars, setCars] = useState([]);

  function sortCars(cars, sortingType="Car Group") {
    const sortedCars = [...cars]; // Create a new array

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
    setCars(sortedCars);
  }

  function fetch_data() {
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

      setData(xlData);
    }

    reader.readAsArrayBuffer(file);
  }

  function normalize_date(date) {

    if (!date) {
      return "None";
    }

    let date_string = date.toUTCString();
    let date_array = date_string.split(' ');
    let year = date_array[3].substring(2, 4);
    let month = date_array[2];

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

    let day = (Number(date_array[1])+1).toLocaleString('en-US', {
      minimumIntegerDigits: 2,
      useGrouping: false
    });
    return `${day}/${month}/${year}`;
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

  function get_overdue_kilometers() {

    let cars = [];

    const Service_offset = 700;

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["Registration Number"] === "BT28627") {
        continue;
      }

      const current_mileage = Number(car["Vehicle Mileage"]) + Service_offset;
      const key_mileage = Number(car["Ignition Key"].substring(3, 8));

      if (current_mileage > key_mileage) {
        if (car["STATUS3"].indexOf("BB") === -1 && car["Checkout Location Mne"] !== "E9Z" && car["Checkout Location Mne"] !== "R4S") {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars);
  }

  function get_overdue_RA() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      // FIX 36 TIMER FØR OVERDUE!

      // if (length !== "NaN") { 
      //   let curDate = new Date().toUTCString().substring(5, 25);
      //   console.log(curDate + " - " + car["Checkin Datetime"].toUTCString().substring(5, 25))
      //   if (car["Rental Agreement Num"].length === 10 && car["Checkin Datetime"] < curDate) {
      //     cars.push(data[i]);
      //   } else if (car["Rental Agreement Num"].length === 9 && car["Checkin Datetime"] < curDate) {
      //     cars.push(data[i]);
      //   }
      // }
      if (length !== "NaN") {
        if (car["Rental Agreement Num"].length === 10 && car["Checkin Datetime"] < new Date() || car["Rental Agreement Num"].length === 9 && car["Checkin Datetime"] < new Date()) {
          cars.push(data[i]);
        }
      }
    }

    sortCars(cars);
  }

  function get_buy_back() {
    let cars = [];

    const BB_number_offset = 5000;

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      if (car["STATUS3"].indexOf("BB") !== -1 || ((car["Ignition Key"].substring(3, 8) >= Number(car["Ignition Key"].substring(0, 2))*1000) && car["Vehicle Mileage"] + BB_number_offset >= (Number(car["Ignition Key"].substring(0, 2))*1000).toString())) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_registration() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Registration Date"] < new Date()) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_inspection() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Inspection Date"] < new Date()) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_disposal() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Disposal Date"] < new Date()) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_status() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["STATUS3"].length > 0) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_all(station) {

    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (station === "NaN") {
        cars.push(data[i]);
      } else {
        if (car["Location Due Mne"] === station || car["Current Location Mne"] === station) {
          cars.push(data[i]);
        }
      }
    }
    sortCars(cars);
  }

  function get_tyres(tyre) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Trunk Key"].substring(0, 1) === tyre) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_accessory(accessory) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      let found = false;
      for (let j = 1; j < 10; j++) {
        if (car["Accessory 0" + j.toString()] === accessory && !found) {
          cars.push(data[i]);
          found = true;
        }
      }
    }
    sortCars(cars);
  }

  function get_payment_method(Method) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
      if (car["Creditclub Code"] === Method && (car["Current Status"] !== "ON HAND" && car["Current Status"] !== "UNAVAILABLE")) {
        cars.push(data[i]);
      }
    }
    sortCars(cars);
  }

  function get_RA(length) {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]

      
      if (length === "NaN") {
        if (car["Rental Agreement Num"].length !== 10 && car["Rental Agreement Num"].length !== 9) {
          cars.push(data[i]);
        }
      } else {
        if (car["Rental Agreement Num"].length === Number(length)) {
          cars.push(data[i]);
        }
      } 
    }
    sortCars(cars);
  }

  function get_out_of_town_cars() {
    let cars = [];

    for (let i = 0; i < data.length; i++) {
      let car = data[i]
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
    sortCars(cars);
  }

  return (
    <>
      {data.length === 0 && <input 
        type="file" 
        id="file-input"
        onChange={() => fetch_data()}
        className='file-input'
      />}

      {data.length > 0 && 
        <div className="logo-container">
          <img src={logo} alt="Avis Logo" className="logo"/>
        </div>
      }

      <div className="main-container">

        <section className="top-area">
          <Selection title="All"                func={get_all} />
          <Selection title="Service"            func={get_overdue_kilometers} />
          <Selection title="Overdue RA/VTC"     func={get_overdue_RA} />
          <Selection title="Buy Back"           func={get_buy_back} />
          <Selection title="Tyres"              func={get_tyres} />
          <Selection title="Accessory"          func={get_accessory} />
          <Selection title="Credentials"        func={get_payment_method}/>
          <Selection title="RA/VTC"             func={get_RA}/>
          <Selection title="Out of Town"        func={get_out_of_town_cars}/>
        </section>

        <section className="bottom-area">
          <table className="table">
            <Table_Head cars={cars} sortCars={sortCars}/>
            <Table_Body cars={cars} normalize_date={normalize_date} fix_duplicate_status={fix_duplicate_status} />
            <Table_Summary cars={cars}/>
          </table>
        </section>
		  </div>
    </>
  )
}

function Table_Head({ cars, sortCars }) {
  return (
    <thead className="table-head">
      <tr className="table-head-row">
        <th onClick={() => sortCars(cars, "Body Type")}>TYPE</th>
        <th onClick={() => sortCars(cars, "Make / Model")}>MODEL</th>
        <th onClick={() => sortCars(cars, "MVA")}>MVA</th>
        <th onClick={() => sortCars(cars, "Registration Number")}>REG</th>
        <th onClick={() => sortCars(cars, "Current Status")}>STATUS</th>
        <th onClick={() => sortCars(cars, "Current Location Mne")}>CUR STA</th>
        <th onClick={() => sortCars(cars, "Location Due Mne")}>IN STA</th>
        <th onClick={() => sortCars(cars, "Checkin Datetime")}>CHECKIN</th>
        <th onClick={() => sortCars(cars, "Car Group")}>GROUP</th>
        <th onClick={() => sortCars(cars, "Vehicle Mileage")}>KM</th>
        <th onClick={() => sortCars(cars, "Ignition Key")}>IGNIT KEY</th>
        <th onClick={() => sortCars(cars, "Rental Agreement Num")}>MOVEMENT</th>
        <th onClick={() => sortCars(cars, "Trunk Key")}>TRUNK KEY</th>
        <th onClick={() => sortCars(cars, "STATUS3")}>STATUS</th>
      </tr>
    </thead>
  )
}

function Table_Body({ cars, normalize_date, fix_duplicate_status }) {

  function displayLoc(car) {
    if (car["Rental Agreement Num"].length === 0) {
      return "";
    } else {
      return car["Location Due Mne"];
    }
  }

  function format_time(time) {

    let month = time.substring(3, 6);
  
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
    
    let day = time.substring(0, 2);
    let year = time.substring(7, 11);

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
          <td>{car["Registration Number"]}</td>
          <td
          style={{
            backgroundColor: Colors[car["Current Status"]]
          }}
          >{car["Current Status"]}</td>
          <td>{car["Current Location Mne"]}</td>
          <td>{displayLoc(car)}</td>
          <td>{format_time(car["Checkin Datetime"].toUTCString().substring(5, 22))}</td>
          <td>{car["Car Group"]}</td>
          <td>{car["Vehicle Mileage"]}</td>
          <td>{car["Ignition Key"]}</td>
          <td>{car["Rental Agreement Num"].substring(1)}</td>
          <td>{car["Trunk Key"]}</td>
          <td>{fix_duplicate_status(car["STATUS3"])}</td>
        </tr>
      ))}
    </tbody>
  )
}

function Table_Summary({ cars }) {

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

  return (
    <tfoot className="table-summary">
      <tr className="table-summary-row">
        <td>Cars: {cars.length}</td>
        <td>RA: {get_num_of_RA(cars)}</td>
        <td>VTC: {get_num_of_VTC(cars)}</td>
        <td>Summer Tyres: {get_num_of_summer_tyres(cars)}</td>
        <td>Winter Tyres: {get_num_of_winter_tyres(cars)}</td>
        <td>Spike free Tyres: {get_num_of_spike_free_tyres(cars)}</td>
      </tr>
    </tfoot>
  )
}

function Selection({ title, func }) {

  if (title === "Credentials") {

    const [param, setParam] = useState("CX");

    return (
      <div className="selection">
        <p>{title}</p>
        <select onChange={(e) => setParam(e.target.value)}>
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
      
    const [param, setParam] = useState("NV");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='accessory-selection' onChange={(e) => setParam(e.target.value)}>
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
    
    const [param, setParam] = useState("P");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='tyre-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="P">VINTER</option>
          <option value="V">PIGGFRITT</option>
          <option value="S">SOMMER</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "RA/VTC") {

    const [param, setParam] = useState("10");

    return (
      <div className="selection">
        <p>{title}</p>
        <select className='RA-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="10">RA</option>
          <option value="9">VTC</option>
          <option value="NaN">NONE</option>
        </select>
        <SearchButton func={func} param={param} />
      </div>
    )
  } else if (title === "All") {
    const [param, setParam] = useState("TR7");
    return (
      <div className="selection">
        <p>{title}</p>
        <select className='station-selection' onChange={(e) => setParam(e.target.value)}>
          <option value="TOS">TOS</option>
          <option value="TR7">TR7</option>
          <option value="TO0">TO0</option>
          <option value="TO7">TO7</option>
          <option value="T1Y">T1Y</option>
          <option value="T6O">T6O</option>
          <option value="R4S">R4S</option>
          <option value="E9Z">E9Z</option>
          <option value="NaN">ALL</option>
        </select>
        <SearchButton func={func} param={param} />
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
