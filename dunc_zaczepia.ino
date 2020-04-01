#include <Servo.h>
// create servo object to control a servo
Servo nogaL;
Servo nogaR;
Servo rekaL;
Servo rekaR;
Servo obrot;
Servo konczyna;
int CAM_WITDH_PXL_MAX = 600;
int CAM_WITDH_PXL_MIN = 0;
int konczynaIndex = 0;
bool test = true;
// ..............0  ,1  ,2  ,3  ,4  ,5  ,6  ,7  ,8  ,9  ,:  ,;
int degVals[] = {
    0,   // 0
    18,  // 1
    36,  // 2
    54,  // 3
    72,  // 4
    90,  // 5
    108, // 6
    126, // 7
    144, // 8
    162, // 9
    180  // :
};

int pauseVals[] = {
    12,   // 0
    25,   // 1
    50,   // 2
    100,  // 3
    150,  // 4
    200,  // 5
    300,  // 6
    400,  // 7
    800,  // 8
    1000, // 9
    1600, // :
    3200, // ;
};

Servo konczyny[] = {
    nogaL,
    nogaR,
    rekaL,
    rekaR,
    obrot};

int prevXpxl[] = {
    300,
    300,
    300,
    300,
    300};
int limbMaxArr[] = {
    130,
    130,
    130,
    130,
    130,
};
int limbMinArr[] = {
    50,
    50,
    50,
    50,
    50,
};
// servoSequencePoint updown90[] = {{0, 0}, {180, 0}}; // go to position 100 at speed of 20, position 20 speed 20, position 60, speed 50
// servoSequencePoint updown10[] = {{80, 0}, {100, 0}};

void setup()
{
    while (!Serial)
        ; // wait for serial port to connect. Needed for native USB port only
    Serial.begin(9600);
    Serial.println("\n Starting");
    Serial.println("\n Resetting servoes to 90");
    obrot.attach(3);
    nogaL.attach(5);
    nogaR.attach(6);  // attaches the servo on pin 9 to the servo object
    rekaL.attach(10); // attaches the servo on pin 9 to the servo object
    rekaR.attach(11); // attaches the servo on pin 9 to the servo object
    ROTALL(90);

    // reka.sequencePlay(rekaxxtest,8,false,0);
    while (!Serial)
        ; // wait for serial port to connect. Needed for native USB port only

    // send an intro:
    Serial.println("\n\nReady to accept programs:");
    Serial.println();
}

void ROTALL(int pos)
{
    obrot.write(pos);
    nogaL.write(pos);
    nogaR.write(pos);
    rekaL.write(pos);
    rekaR.write(pos);
}

void D(int lng)
{
    delay(lng);
}

void mapIncomingIntPixelsToServoAngle()
{
    int Xpxl = Serial.parseInt();
    if (Xpxl != prevXpxl[konczynaIndex]) // only if new data is sent for this limb start moving
    {
        prevXpxl[konczynaIndex] = Xpxl;          // store new data for later comparison
        int limbMax = limbMaxArr[konczynaIndex]; // TODO: encaps in class Maximum servo position for limb
        int limbMin = limbMinArr[konczynaIndex]; // TODO: encaps in class Minimum servo position for limb

        int limbPos = map(Xpxl, CAM_WITDH_PXL_MAX, CAM_WITDH_PXL_MIN, limbMin, limbMax); // map pixel coordinate to corresponding servo angle
        // if mapped result exceeds extrema of servo range, cap it to extrema
        limbPos = min(limbPos, limbMax);
        limbPos = max(limbPos, limbMin);
        konczyna.write(limbPos);
    }
}

void ruszKonczyna()
{
    char c = Serial.read();
    if (c == '=') // if character = detected treat incoming value as pixels
    {
        return mapIncomingIntPixelsToServoAngle();
    }
    int ii = c - 48;
    if (ii > 10 || ii < 0)
    {
        Serial.print("blad nie ma wartosci stopni dla ");
        Serial.println(ii);
    }
    else
    {
        int pos = degVals[ii];
        konczyna.write(pos);
    }
}

void pauzuj()
{

    char c = Serial.read();
    int ic = c;
    Serial.print("paramater for pause : ");
    Serial.print(c);
    Serial.print("->");
    Serial.print(" ascii code: ");
    Serial.println(ic);
    if (ic == -1)
    {
        return pauzuj(); // WTH ? this is monkey patch for removing mirrored '?' sign with value of -1 trailing after p character.
    }
    if (c == '=')
    {
        int dlugo = Serial.parseInt();
        Serial.print("Dokladne - pauzuje na tyle ms:");
        Serial.println(dlugo);
        delay(dlugo);
        Serial.flush();
        return;
        // todo parse int and treat it as amount of miliseconds
        // make sure there is no mistake with limbs
    }
    else
    {

        int ii = ic - 48;
        if (ii > 11 || ii < 0)
        {
            Serial.print("blad nie ma wartosci pauzy dla ");
            Serial.print(c);
            Serial.print(" -> ");
            Serial.println(ii);
            Serial.flush();
            return;
        }
        else
        {

            int dlugo = pauseVals[ii];
            Serial.print("pauzuje na tyle ms:");
            Serial.println(dlugo);
            delay(dlugo);
        }
    }
}

void testAll()
{
    ROTALL(90);
        delay(500);
        ROTALL(80);
        delay(500);
        ROTALL(90);
        delay(500);
        ROTALL(100);
        delay(500);
}

void loop()
{
    if (test == true)
    {
        testAll();
    }

    while (Serial.available() > 0)
    {
        test = false;
        Serial.println("wprowadzono program");
        char c = Serial.read();
        int ic = c;
        Serial.print("You entered: ");
        Serial.print(c);
        Serial.print("->");
        Serial.print(" ascii code: ");
        Serial.println(ic);
        int ii = c;
        switch (c)
        {
        case 't':
            Serial.println("test wszystkiego");
            testAll();
            finishProg();
            return;
            break;
        case 'l': // 0 left hand
            Serial.println("ruch lewa reka");
            konczyna = rekaL;
            konczynaIndex = 0;
            ruszKonczyna();
            break;
        case 'r': // 1 right hand
            Serial.println("ruch prawa reka ");
            konczyna = rekaR;
            konczynaIndex = 1;
            ruszKonczyna();
            break;
        case 'n': // 2 left leg
            Serial.println("ruch lewa noga");
            konczyna = nogaL;
            konczynaIndex = 2;
            ruszKonczyna();
            break;
        case 'm': // 3 right leg
            Serial.println("ruch prawa noga");
            konczyna = nogaR;
            konczynaIndex = 3;
            ruszKonczyna();
            break;
        case 'd': // 4 rotate obrot

            Serial.println("ruch obrot");
            // TODO: here you could do something to prevent stall if other servos being above their extrema (limbs must be l3 to l5 in order for d to move)
            konczyna = obrot;
            konczynaIndex = 4;
            ruszKonczyna();
            break;
        case 'p': // p pause
            Serial.println("pauza");
            pauzuj();
            continue;
            break;
        case '-':
            Serial.println("--------------------");
        case ' ':
        case ',':
        case 10:
            continue;
            break;
        default:
            Serial.print("blad nie ma konczyny albo polecenia nr ");
            Serial.println(c);
            finishProg();
            return;
        }
    }
}

void finishProg()
{
    test = true;
    Serial.flush();
}
// l2r8d2p4l8r2p1l2r8p1l8r2d8p1l8r2p1l2r8p1
// l2 r8 d2 p4, l8 r2 p1, l2 r8 p1, l8 r2 d8 p1, l8 r2 p1, l2 r8 p1
// l2 r8 n2 m8 --d4 p1, l8 r2 n8 m2 p1, l2 r8 n2 m8 p1, l8 r2 n5 m5 -- d8 p1, l8 r2 n2 m2 p1, l2 r8 p1
// l1r8n1m8d1p0 l8r1n8m1d8p0 l1r8n1m8d1p0 l8r1n8m1d8p0 l1r8n1m8d1p0 l8r1n8m1d8p0 l1r8n1m8d1p0 l8r1n8m1d8p0
// test reki
// p:r2p9r8p9r1p3r:p3r2p9r8p9r1p3r:p3
// test wszystkiego
// l4p5l6p5 r4p5r6p5 n4p5n6p5 m4p5m6p5 d4p5d6p5
// l4p5l6p5 r4p5r6p5 n4p5n6p5 m4p5m6p5 d2p9d8p9

// odwraca sie i macha reka
// d1p: l8p1 d2p1 l2p1 d3p1 l8p1 d4p1 l2p1 d5p1 l8p1 d6p1 l2p1 d7p1 l8p1 d8p1 l2p1 d9p1 l8p1 d:p1 l2p1
// odwraca sie macha reka i noga  -- dziala
// l2d: p:p: l6 d0 l2 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0
// do scenki
// p: l2d: p:p: l6 d0 l2 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 l6p0 l2p0 p:
