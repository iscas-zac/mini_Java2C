struct String {
char upperExpand[100];
char upperSpecial[100];
char value[100];
int count;
int offset;
};
struct String s = { .value = "", .offset = 0 };
struct String s1 = { .value = "111", .offset = 0 };
int v;
if (!(s1 instanceof String))
v = false;
String str2 = (String) s1;
if (s.count != str2.count)
v = false;
if (s.value == str2.value && offset == str2.offset)
v = true;
int i = s.count;
int x = s.offset;
int y = str2.offset;
while (--i >= 0)
if (s.value[x++] != str2.value[y++])
@(v);