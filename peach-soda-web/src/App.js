import React, { useState, useEffect } from 'react';
import './App.css';
import { makeStyles } from '@material-ui/core/styles';
import {AppBar, Toolbar, Tabs, Typography, IconButton, Tab} from '@material-ui/core'
import Homepage from './components/homepage';
import AddSuggestion from './components/addSuggestions';
import ViewSuggestion from './components/viewSuggestions';
import { getSuggestionsEndpoint, postSuggestionEndpoint, putASuggestionIntoUsedModeEndpoint, putASuggestionIntoActiveModeEndpoint, postASuggestionRemovalEndpoint, postANewUserEndpoint, postAUserRemovalEndpoint} from './config/endpoints';

function App() {
  const [value, setValue] = useState(0);
  const [suggestionList, setSuggestionList] = useState([]);
  // useEffect(()=>{
  //   window.fetch(getSuggestionsEndpoint(), {method: 'GET'})
  //   .then(res => res.json())
  //   .then((result)=> {
  //     setSuggestionList(result)
  //   })
  // })
  const useStyles = makeStyles((theme) => ({
    root: {
      flexGrow: 1,
    },
    menuButton: {
      marginRight: theme.spacing(2),
    },
    title: {
      flexGrow: 1,
    },
  }));
  const classes = useStyles();
  function a11yProps(index) {
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`,
    };
  }
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  return (
    <div className="App">
      <AppBar position="static" className="app-bar">
        <Toolbar>
          <Tabs value={value} onChange={handleChange} aria-label="simple tabs example" >
            <Tab label="Homepage" {...a11yProps(0)} />
            <Tab label="Add suggestion" {...a11yProps(1)} />
            <Tab label="View suggestions" {...a11yProps(2)} />
          </Tabs>
          <Typography variant="h6" className={classes.title}>
            Peach Soda
          </Typography>
        </Toolbar>
      </AppBar>
      {(value===0) && <Homepage />}
      {(value===1) && <AddSuggestion />}
      {(value===2) && <ViewSuggestion />}
    </div>
  );
}

export default App;
