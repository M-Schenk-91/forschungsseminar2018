//We always have to include the library
#include "LedControl.h"

/*
  Now we need a LedControl to work with.
 ***** These pin numbers will probably not work with your hardware *****
  pin 12 is connected to the DataIn
  pin 11 is connected to the CLK
  pin 10 is connected to LOAD
  We have only a single MAX72XX.
*/
LedControl lc = LedControl(D7, D5, D2, 1);

/* we always wait a bit between updates of the display */
unsigned long delaytime = 100;

const int BUTTON = D3;
const int NUM_MATRICES = 3;

int button_presses = 0;

bool is_button_pressed = false;

void setup() {
  pinMode(BUTTON, INPUT);

  Serial.begin(9600);

  /*
    The MAX72XX is in power-saving mode on startup,
    we have to do a wakeup call
  */
  lc.shutdown(0, false);
  /* Set the brightness to a medium values */
  lc.setIntensity(0, 8);
  /* and clear the display */
  lc.clearDisplay(0);
}

/*
  This method will display the characters for the
  word "Arduino" one after the other on the matrix.
  (you need at least 5x7 leds to see the whole chars)
*/
void writeMarkerMatrix(byte * matrix) {
  /* here is the data for the characters */

  /* now display them one by one with a small delay */
  for (int i = 0; i < 8; i++)
    lc.setRow(0, i, matrix[i]);
}

byte a[8] =
{
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000
};

void loop() {
  if (digitalRead(BUTTON) == HIGH)
  {
    if (!is_button_pressed)
    {
      is_button_pressed = true;
      button_presses++;

      switch (button_presses % NUM_MATRICES)
      {
        case 0:
          a[0] = B11111111;
          a[1] = B10000001;
          a[2] = B10111101;
          a[3] = B10011001;
          a[4] = B10100101;
          a[5] = B10111101;
          a[6] = B10000001;
          a[7] = B11111111;
          break;

        case 1:
          a[0] = B11111111;
          a[1] = B10000001;
          a[2] = B10111101;
          a[3] = B10110001;
          a[4] = B10001101;
          a[5] = B10111101;
          a[6] = B10000001;
          a[7] = B11111111;
          break;

        case 2:
          a[0] = B11111111;
          a[1] = B10000001;
          a[2] = B10100101;
          a[3] = B10011001;
          a[4] = B10011001;
          a[5] = B10100101;
          a[6] = B10000001;
          a[7] = B11111111;
          break;
      }
    }
  }
  else
  {
    is_button_pressed = false;
  }

  writeMarkerMatrix(a);
  delay(delaytime);
}
