#include <Servo.h>
// create servo objects to control limbs
Servo nogaL;
Servo nogaR;
Servo rekaL;
Servo rekaR;
Servo obrot;

int SERVOS_COUNT = 5;
// array conatining all servos
Servo konczyny[] = {
    nogaL,
    nogaR,
    rekaL,
    rekaR,
    obrot};
// letters representing above servos in my syntax
char konczyny_letters[] = {
    'n',
    'm',
    'l',
    'r',
    'd',
};

Servo konczyna;
int VERBOSITY = 1; // level to set the verbosity of serial messages
const int DEBUGLEVEL = 1;
int CAM_WITDH_PXL_MAX = 335; // because face is never on the edge  // was 400
int CAM_WITDH_PXL_MIN = 65;  // was 0 . see above
int konczynaIndex = 0;       // currently moved limb/servo index
bool test = false;
bool modetest = false;

// ..............0  ,1  ,2  ,3  ,4  ,5  ,6  ,7  ,8  ,9  ,:  ,;
// these values represent degree values for custom servo programming syntax
// one character value instead of providing full degree value
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
// similarly those pause values allow to program robot with concise one-char commands
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
// theses arrays provide storage for previous values written to servos (redundant since (servo.read()))
int prevXpxl[] = {300, 300, 300, 300, 300};
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
// encapsulating serial output to provide debug channel
void debug(String ZXC)
{
    if (VERBOSITY >= DEBUGLEVEL)
    {
        Serial.print(ZXC);
    }
}

void debug(int ZXC)
{
    if (VERBOSITY >= DEBUGLEVEL)
    {
        Serial.print(ZXC);
    }
}

void debugln(int ZXC)
{
    if (VERBOSITY >= DEBUGLEVEL)
    {
        Serial.println(ZXC);
    }
}

void debugln(const char *ZXC)
{
    if (VERBOSITY >= DEBUGLEVEL)
    {
        Serial.println(ZXC);
    }
}

void setup()
{
    while (!Serial)
        ;
    Serial.begin(9600);
    debugln("\n Starting");
    debugln("\n Resetting servoes to 90");
    obrot.attach(3);
    nogaL.attach(10);
    nogaR.attach(11);
    rekaL.attach(5);
    rekaR.attach(6);
    ROTALL(90);

    // send an intro:
    debugln("\n\nReady to accept programs:\n");
}

void ROTALL(int pos)
{
    obrot.write(pos);
    nogaL.write(pos);
    nogaR.write(pos);
    rekaL.write(pos);
    rekaR.write(pos);
}

void mapIncomingIntPixelsToServoAngle()
{
    int Xpxl = Serial.parseInt();        // parse int after already parsed limb token ( "l=300")
    if (Xpxl != prevXpxl[konczynaIndex]) // only if new data is sent for this limb start moving
    {
        prevXpxl[konczynaIndex] = Xpxl;          // store new data for later comparison
        int limbMax = limbMaxArr[konczynaIndex]; // TODO: encaps in class Maximum servo position for limb
        int limbMin = limbMinArr[konczynaIndex]; // TODO: encaps in class Minimum servo position for limb

        int limbPos = map(Xpxl, CAM_WITDH_PXL_MAX, CAM_WITDH_PXL_MIN, limbMin, limbMax); // map pixel coordinate to corresponding servo angle
        // if mapped result exceeds extrema of servo range, cap it to extrema
        // limbPos = min(limbPos, limbMax);
        // limbPos = max(limbPos, limbMin);
        konczyna.write(limbPos);
    }
}

// if character specifies that following int is exact degree value
void writeInDegrees()
{
    konczyna.write(Serial.parseInt());
}

//detects what method should be used to interpret limb movement command
void ruszKonczyna()
{
    char c = Serial.read();
    if (c == '=') // if character = detected treat incoming value as pixels
    {
        return mapIncomingIntPixelsToServoAngle();
    }
    if (c == '$')
    {
        return writeInDegrees();
    }
    int ii = c - 48;
    if (ii > 10 || ii < 0) // if value symbol is not translated to index within values array 1 to :
    {
        debug("blad nie ma wartosci stopni dla ");
        debugln(ii);
    }
    else
    {
        int pos = degVals[ii];
        konczyna.write(pos);
    }
}
// this is run if the token specyfyong pause os detected
void pauzuj()
{

    char c = Serial.read();
    int ic = c;
    debug("paramater for pause : ");
    debug(c);
    debug("->");
    debug(" ascii code: ");
    debugln(ic);
    if (ic == -1)
    {
        return pauzuj(); // WTH ? this is monkey patch for removing mirrored '?' sign with value of -1 trailing after p character. Baud rate is ok so how?
    }
    if (c == '$')//exact pause character
    {
        int dlugo = Serial.parseInt();
        debug("Dokladne pauzowanie - pauzuje na tyle ms:");
        debugln(dlugo);
        delay(dlugo);
        return;
        // todo parse int and treat it as amount of miliseconds
        // make sure there is no mistake with limbs
    }
    else
    {

        int ii = ic - 48;
        if (ii > 11 || ii < 0)
        {
            debug("blad nie ma wartosci pauzy dla ");
            debug(c);
            debug(" -> ");
            debugln(ii);
            return;
        }
        else
        {

            int dlugo = pauseVals[ii];
            debug("pauzuje na tyle ms:");
            debugln(dlugo);
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
        delay(1); // without it there seems to be some porblem with executing commands
        // without one milisecond delay commands are not executing as intended
        test = modetest;
        debugln("wprowadzono program");
        char c = Serial.read();
        int ic = c;
        debug("You entered: ");
        debug(c);
        debug("->");
        debug(" ascii code: ");
        debugln(ic);
        int ii = c;
        switch (c)
        {
        case 'v':
            if (VERBOSITY == 1)
            {
                debugln("wylaczam debugging");
                VERBOSITY = 0;
            }
            else if (VERBOSITY == 0)
            {
                VERBOSITY = 1;
                debugln("wlaczam debugging");
            }
            break;
        case 's':
            debugln('reset all to 90');
            ROTALL(90);
            finishProg();
            return;
            break;
        case '*':
            debugln('these are all positions');
            for (int idx = 0; idx < SERVOS_COUNT; idx++)
            {
                int pos = konczyny[idx].read();
                char letter = konczyny_letters[idx];
                Serial.print(letter);
                Serial.print(":");
                Serial.println(pos);
            }
            // TODO loop through servos and output positons by calling
            // on each
            // https://forum.arduino.cc/index.php?topic=526154.0

            finishProg();
            return;
            break;
        case 't':
            debugln("test wszystkiego");
            testAll();
            finishProg();
            return;
            break;
        case 'l': // 0 left hand
            debugln("ruch lewa reka");
            konczyna = rekaL;
            konczynaIndex = 0;
            ruszKonczyna();
            break;
        case 'r': // 1 right hand
            debugln("ruch prawa reka ");
            konczyna = rekaR;
            konczynaIndex = 1;
            ruszKonczyna();
            break;
        case 'n': // 2 left leg
            debugln("ruch lewa noga");
            konczyna = nogaL;
            konczynaIndex = 2;
            ruszKonczyna();
            break;
        case 'm': // 3 right leg
            debugln("ruch prawa noga");
            konczyna = nogaR;
            konczynaIndex = 3;
            ruszKonczyna();
            break;
        case 'd': // 4 rotate obrot

            debugln("ruch obrot");
            // TODO: here you could do something to prevent stall if other servos being above their extrema (limbs must be l3 to l5 in order for d to move)
            konczyna = obrot;
            konczynaIndex = 4;
            ruszKonczyna();
            break;
        case 'p': // p pause
            debugln("pauza");
            pauzuj();
            continue;
            break;
        case '-':
            debugln("--------------------");
        case ' ':
        case ',':
        case 10:
            continue;
            break;
        default:
            debug("blad nie ma konczyny albo polecenia nr ");
            debugln(c);
            finishProg();
            return;
        }
    }
}

void finishProg()
{
    test = modetest;
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
