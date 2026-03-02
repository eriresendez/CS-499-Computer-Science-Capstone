package com.example.erickaresendezeventtrackingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;

import com.example.erickaresendezeventtrackingapp.database.entity.EventItem;
import com.example.erickaresendezeventtrackingapp.viewmodel.EventItemViewModel;
import com.example.erickaresendezeventtrackingapp.repository.EventItemRepository;

import java.util.Calendar;

public class AddingData extends AppCompatActivity {
    private EventItemViewModel eventItemViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_adding_data);

        // Initialize ViewModel
        eventItemViewModel = new ViewModelProvider(this).get(EventItemViewModel.class);

        EditText eventName = findViewById(R.id.editEventName);
        DatePicker datePicker = findViewById(R.id.datePickerEvent);
        EditText eventDescription = findViewById(R.id.editEventDescription);
        Button saveButton = findViewById(R.id.buttonSaveEvent);
        Button cancelButton = findViewById(R.id.buttonCancel);

        cancelButton.setOnClickListener(v -> finish());

        saveButton.setOnClickListener(v -> {
            String name = eventName.getText().toString().trim();
            String description = eventDescription.getText().toString().trim();

            if (name.isEmpty()) {
                Toast.makeText(this, "Please enter an event name", Toast.LENGTH_SHORT).show();
                return;
            }

            // Read date from the DatePicker widget
            int year = datePicker.getYear();
            int month = datePicker.getMonth();
            int day = datePicker.getDayOfMonth();
            Calendar cal = Calendar.getInstance();
            cal.set(year, month, day, 0, 0, 0);
            cal.set(Calendar.MILLISECOND, 0);
            long eventTimestamp = cal.getTimeInMillis();

            // Get logged-in user ID
            SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
            int currentUserId = prefs.getInt("current_user_id", -1);

            if (currentUserId == -1) {
                Toast.makeText(this, "Session error, please log in again", Toast.LENGTH_SHORT).show();
                return;
            }

            EventItem newItem = new EventItem(name, 1, currentUserId);
            newItem.setDescription(description);
            newItem.setEventDate(eventTimestamp);

            eventItemViewModel.insertItem(newItem, new EventItemRepository.InsertCallback() {
                @Override
                public void onSuccess(int itemId) {
                    runOnUiThread(() -> {
                        Toast.makeText(AddingData.this, "Event saved!", Toast.LENGTH_SHORT).show();
                        finish();
                    });
                }

                @Override
                public void onError(String error) {
                    runOnUiThread(() ->
                            Toast.makeText(AddingData.this, "Error: " + error, Toast.LENGTH_SHORT).show());
                }
            });
        });
    }
}